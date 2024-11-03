import re
from dataclasses import dataclass, field
from typing import BinaryIO

import numpy as np
from hifitime import Epoch, TimeScale

from .code import Code
from .delay import SystemDelay
from .reftime import UTC, ReferenceTime
from .track import Track
from .version import Version

CURRENT_VERSION: str = "2E"


@dataclass
class Coordinates:
    """Coordinates"""

    x: np.float64 = 0.0
    y: np.float64 = 0.0
    z: np.float64 = 0.0

    def __str__(self):
        return f"{self.x} {self.y} {self.z}"


@dataclass
class File:
    """A CGGTTS data structure.

    Contains a list of comparisons between a local clock and a reference time system.

    Attributes:
        version: CGGTTS version used in this file. We only support version 2E (latest)
        release_date: The release date of the CGGTTS file.
        station: The station name.
        receiver: GNSS receiver info.
        num_channels: The number of GNSS receiver channels.
        ims: Ionospheric Measurement System used, if any.
        reference_time: The reference time system.
        reference_frame: The reference frame, coordinates system and conversions.
        apc_coordinates: Antenna phase center coordinates in meters.
        comments: Comments, if any.
        delay: System delay.
        tracks: List of succesive measurements.
    """

    version: Version = Version.VERSION_2E
    release_date: Epoch | None = field(
        default_factory=Epoch.init_from_gregorian_at_midnight(
            2014, 2, 20, TimeScale.UTC
        )
    )
    station: str = "LAB"
    receiver: str | None = None
    num_channels: np.uint16 = 0
    ims: str | None = None
    reference_time: ReferenceTime = field(default_factory=ReferenceTime(UTC()))
    reference_frame: str | None = None
    apc_coordinates: Coordinates = field(default_factory=Coordinates())
    comments: str | None = None
    delay: SystemDelay = field(default_factory=SystemDelay())
    tracks: list[Track] = field(default_factory=list)


def load(fp: BinaryIO) -> File:
    """Load a CGGTTS file from a binary stream.

    Args:
        BinaryIO: A binary stream.

    Returns:
        A CGGTTS file.
    """
    b = fp.read()

    try:
        s = b.decode()
    except AttributeError:
        raise TypeError(
            "File must be opened in binary mode, e.g. use `open('file', 'r')`"
        ) from None

    return loads(s)


def loads(s: str) -> File:
    lines = iter(s.splitlines())

    # Initialize variables
    release_date = None
    num_channels = 0
    receiver = None
    ims = None
    station = "LAB"
    comments = None
    system_delay = SystemDelay()
    reference_time = ReferenceTime(UTC())
    reference_frame = None
    apc_coordinates = Coordinates()

    # Version always comes first
    line = next(lines)
    if line.strip() == "RAW CLOCK RESULTS":
        version = Version.RAW
    else:
        m = re.match(r"CGGTTS\s+GENERIC DATA FORMAT VERSION = (\w+)", line)
        match m:
            case None:
                raise ValueError("Version format error.")
            case _:
                version = Version.from_str(m.group(1))

    # Parse the header
    while True:
        line = next(lines)

        if line.startswith("REV DATE = "):
            m = re.match(r"REV DATE = (\d{4})-(\d{2})-(\d{2})", line)
            match m:
                case None:
                    raise ValueError("Release date format error.")
                case _:
                    release_date = Epoch.init_from_gregorian_at_midnight(
                        int(m.group(1)),
                        int(m.group(2)),
                        int(m.group(3)),
                        TimeScale.UTC,
                    )
        elif line.startswith("RCVR = "):
            # TODO: Correctly parse receiver info
            m = re.match(r"RCVR = (\w+)", line)
            match m:
                case None:
                    continue
                case _:
                    receiver = m.group(1)
        elif line.startswith("CH = "):
            m = re.match(r"CH = (\d+)", line)
            match m:
                case None:
                    continue
                case _:
                    num_channels = np.uint16(m.group(1))
        elif line.startswith("IMS = "):
            m = re.match(r"IMS = (\w+) (\w+) (\w+) (\d+) (\w+)", line)
            match m:
                case None:
                    continue
                case _:
                    ims = m.group(1)
        elif line.startswith("LAB = "):
            match line.strip("LAB = "):
                case "":
                    continue
                case s:
                    station = s.strip()
        elif line.startswith("X = "):
            m = re.match(r"X =\s+([+-]?\d+\.\d+)", line)
            match m:
                case None:
                    continue
                case _:
                    apc_coordinates.x = np.float64(m.group(1))
        elif line.startswith("Y = "):
            m = re.match(r"Y =\s+([+-]?\d+\.\d+)", line)
            match m:
                case None:
                    continue
                case _:
                    apc_coordinates.y = np.float64(m.group(1))
        elif line.startswith("Z = "):
            m = re.match(r"Z =\s+([+-]?\d+\.\d+)", line)
            match m:
                case None:
                    continue
                case _:
                    apc_coordinates.z = np.float64(m.group(1))
        elif line.startswith("FRAME = "):
            f = line[7:].strip()
            if f != "?":
                reference_frame = f
        elif line.startswith("COMMENTS = "):
            c = line.strip("COMMENTS = ").strip()
            if c and c != "NO COMMENTS":
                comments = c
        elif line.startswith("REF = "):
            m = re.match(r"REF = (.+)", line)
            match m:
                case None:
                    continue
                case _:
                    reference_time = ReferenceTime.from_str(m.group(1))
        elif "DLY = " in line:
            items = line.split()
            dual_carrier = "," in line

            if len(items) < 4:  #  Format mismatch
                continue

            match items[0]:
                case "CAB":
                    system_delay.cab_delay = np.float64(items[3])
                case "REF":
                    system_delay.ref_delay = np.float64(items[3])
                case "SYS":
                    if "CAL_ID" in line:
                        offset = line.rfind("=")
                        cal_id = line[offset + 1 :].strip()
                        if cal_id != "NA":
                            system_delay.cal_id = cal_id

                    if dual_carrier:
                        value = np.float64(items[3])
                        code = items[6].replace("),", "")

                        # TODO: Iterate over all codes
                    elif value := np.float64(items[3]):
                        code = items[6].replace("),", "")
                        if code := Code[code]:
                            system_delay.delays[code] = value
                case "INT":
                    if "CAL_ID" in line:
                        offset = line.rfind("=")
                        cal_id = line[offset + 1 :].strip()
                        if cal_id and cal_id != "NA":
                            system_delay.cal_id = cal_id

                    if dual_carrier:
                        value = np.float64(items[3])
                        code = items[6].replace("),", "")

                        # TODO: Iterate over all codes
                    elif value := np.float64(items[3]):
                        code = items[6].replace("),", "")
                        if code := Code[code]:
                            system_delay.delays[code] = value
                case _:
                    continue
        elif line.startswith("CKSUM = "):
            # TODO: Process checksum
            break

    # Skip lines (blank, labels, units)
    next(lines)
    next(lines)
    next(lines)

    # Parse tracks
    tracks = []
    while True:
        try:
            line = next(lines)
            if line == "":  # We are done parsing
                break

            tracks.append(Track.from_str(line))
        except StopIteration:  # EOF
            break

    return File(
        version=version,
        release_date=release_date,
        station=station,
        receiver=receiver,
        num_channels=num_channels,
        ims=ims,
        reference_time=reference_time,
        reference_frame=reference_frame,
        apc_coordinates=apc_coordinates,
        comments=comments,
        delay=system_delay,
        tracks=tracks,
    )
