import types
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterator

import numpy as np
from hifitime import Duration, Epoch, Unit

TrackType = types.SimpleNamespace()
TrackType.WITH_IONO = 24
TrackType.WITHOUT_IONO = 21


class CommonViewClass(StrEnum):
    """Kind of Common View system."""

    SINGLE = "99"
    MULTI = "FF"


@dataclass
class IonosphericData:
    """Ionospheric data attached to a CGGTTS track.

    Attributes:
        msio: Measured ionospheric delay in nanoseconds.
        smsi: Slope of the measured ionospheric delay in picoseconds per second.
        isg: Root-mean-square of the residuals in nanoseconds.
    """

    msio: np.float64
    smsi: np.float64
    isg: np.float64


@dataclass
class TrackData:
    """Track data.

    Attributes:
        refsv: Difference to the reference SV in nanoseconds.
        srsv: Slope of the reference SV in picoseconds per second.
        refsys: Difference to the reference system in nanoseconds.
        srsys: Slope of the reference system in picoseconds per second.
        dsg: Root-mean-square of the residuals to linear fit in nanoseconds.
        ioe: Three-digit decimal code indicating the ephemeris used for the computation.
        mdtr: Modeled tropospheric delay in nanoseconds.
        smdt: Slope of the modeled tropospheric delay in picoseconds per second.
        mdio: Modeled ionospheric delay in nanoseconds.
        smdi: Slope of the modeled ionospheric delay in picoseconds per second.
    """

    refsv: np.float64
    srsv: np.float64
    refsys: np.float64
    srsys: np.float64
    dsg: np.float64
    ioe: np.uint16
    mdtr: np.float64
    smdt: np.float64
    mdio: np.float64
    smdi: np.float64

    @classmethod
    def _parse_data(cls, items: Iterator[str]):
        refsv = np.float64(next(items)) * 0.1
        srsv = np.float64(next(items)) * 0.1
        refsys = np.float64(next(items)) * 0.1
        srsys = np.float64(next(items)) * 0.1
        dsg = np.float64(next(items)) * 0.1
        ioe = np.uint16(next(items))
        mdtr = np.float64(next(items)) * 0.1
        smdt = np.float64(next(items)) * 0.1
        mdio = np.float64(next(items)) * 0.1
        smdi = np.float64(next(items)) * 0.1

        return cls(refsv, srsv, refsys, srsys, dsg, ioe, mdtr, smdt, mdio, smdi)

    @classmethod
    def parse_without_iono(cls, items: Iterator[str]):
        return cls._parse_data(items), None

    @classmethod
    def parse_with_iono(cls, items: Iterator[str]):
        data = cls._parse_data(items)

        iono = IonosphericData(
            msio=np.float64(next(items)) * 0.1,
            smsi=np.float64(next(items)) * 0.1,
            isg=np.float64(next(items)) * 0.1,
        )
        return data, iono


@dataclass
class Track:
    """A CGGTTS measurement.

    Attributes:
        cv_class: Common View class (Single/Multi channel).
        epoch: Epoch of this track.
        duration: Tracking duration.
        sv: Satellite vehicle tracked.
        elevation: Elevation at track midpoint, expressed in degrees.
        azimuth: Azimuth at track midpoint, expressed in degrees.
        data: Track data.
        iono: Optional ionospheric compensation terms.
        fr: GLONASS channel frequency [1:24], 0 for other GNSS.
        hc: Hardware/receiver channel [0:99], 0 if unknown.
        frc:  Carrier frequency standard 3 letter code.
    """

    cv_class: CommonViewClass
    epoch: Epoch
    duration: Duration
    sv: str
    elevation: np.float64
    azimuth: np.float64
    data: TrackData
    iono: IonosphericData | None
    fr: np.uint8
    hc: np.uint8
    frc: str

    @classmethod
    def from_str(cls, s: str):
        items = s.strip().split()

        num_items = len(items)
        it_items = iter(items)

        sv = next(it_items)
        cv_class = CommonViewClass(next(it_items))
        mjd = np.int32(next(it_items))

        sttime = next(it_items)
        if len(sttime) < 6:
            raise ValueError("Invalid start time format")

        hh = np.uint8(sttime[0:2])
        mm = np.uint8(sttime[2:4])
        ss = np.uint8(sttime[4:6])

        epoch = Epoch.init_from_mjd_utc(np.float64(mjd))
        epoch = epoch + Unit.Hour * np.float64(hh)
        epoch = epoch + Unit.Minute * np.float64(mm)
        epoch = epoch + Unit.Second * np.float64(ss)

        duration = Duration.from_total_nanoseconds(
            (np.float64(next(it_items)) * 1e9).astype(np.int64)
        )

        elevation = np.float64(next(it_items)) * 0.1
        azimuth = np.float64(next(it_items)) * 0.1

        data: TrackData
        iono: IonosphericData
        match num_items:
            case TrackType.WITH_IONO:
                data, iono = TrackData.parse_with_iono(it_items)
            case TrackType.WITHOUT_IONO:
                data, iono = TrackData.parse_without_iono(it_items)
            case _:
                raise ValueError("Invalid number of items")

        fr = np.uint8(next(it_items))
        hc = np.uint8(next(it_items))
        frc = next(it_items)

        # TODO: Process checksum
        _ = next(it_items)

        return cls(
            cv_class, epoch, duration, sv, elevation, azimuth, data, iono, fr, hc, frc
        )
