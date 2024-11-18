import types
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterator

import numpy as np
from hifitime import Duration, Epoch, Unit

TrackType = types.SimpleNamespace()
TrackType.WITH_IONO = 24
TrackType.WITHOUT_IONO = 21
TrackType.RAW = 12


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

    msio: np.float64 | None
    smsi: np.float64 | None
    isg: np.float64 | None


@dataclass
class TrackData:
    """Track data.

    All values expressed in seconds.

    Attributes:
        refsv: Difference to the reference SV.
        srsv: Slope of the reference SV.
        refsys: Difference to the reference system.
        srsys: Slope of the reference system.
        dsg: Root-mean-square of the residuals to linear fit.
        ioe: Three-digit decimal code indicating the ephemeris used for the computation.
        mdtr: Modeled tropospheric delay.
        smdt: Slope of the modeled tropospheric delay.
        mdio: Modeled ionospheric delay.
        smdi: Slope of the modeled ionospheric delay.
    """

    refsv: np.float64
    srsv: np.float64 | None
    refsys: np.float64
    srsys: np.float64 | None
    dsg: np.float64 | None
    ioe: np.uint16
    mdtr: np.float64
    smdt: np.float64 | None
    mdio: np.float64
    smdi: np.float64 | None

    @classmethod
    def _parse_data(cls, items: Iterator[str]):
        refsv = _parse_value(next(items), np.float64, 0.1e-9)
        srsv = _parse_value(next(items), np.float64, 0.1e-12)
        refsys = _parse_value(next(items), np.float64, 0.1e-9)
        srsys = _parse_value(next(items), np.float64, 0.1e-12)
        dsg = _parse_value(next(items), np.float64, 0.1e-9)
        ioe = _parse_value(next(items), np.uint16)
        mdtr = _parse_value(next(items), np.float64, 0.1e-9)
        smdt = _parse_value(next(items), np.float64, 0.1e-12)
        mdio = _parse_value(next(items), np.float64, 0.1e-9)
        smdi = _parse_value(next(items), np.float64, 0.1e-12)

        return cls(refsv, srsv, refsys, srsys, dsg, ioe, mdtr, smdt, mdio, smdi)

    @classmethod
    def parse_without_iono(cls, items: Iterator[str]):
        return cls._parse_data(items), None

    @classmethod
    def parse_with_iono(cls, items: Iterator[str]):
        data = cls._parse_data(items)

        msio = _parse_value(next(items), np.float64, 0.1e-9)
        smsi = _parse_value(next(items), np.float64, 0.1e-12)
        isg = _parse_value(next(items), np.float64, 0.1e-9)

        iono = IonosphericData(msio, smsi, isg)
        return data, iono

    @classmethod
    def parse_raw(cls, items: Iterator[str]):
        refsv = _parse_value(next(items), np.float64, 0.1e-9)
        refsys = _parse_value(next(items), np.float64, 0.1e-9)
        ioe = _parse_value(next(items), np.uint16)
        mdtr = _parse_value(next(items), np.float64, 0.1e-9)
        mdio = _parse_value(next(items), np.float64, 0.1e-9)

        msio = _parse_value(next(items), np.float64, 0.1e-9)

        iono = IonosphericData(msio=msio, smsi=None, isg=None)
        return cls(refsv, None, refsys, None, None, ioe, mdtr, None, mdio, None), iono


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

    cv_class: CommonViewClass | None
    epoch: Epoch
    duration: Duration | None
    sv: str
    elevation: np.float64
    azimuth: np.float64
    data: TrackData
    iono: IonosphericData | None
    fr: np.uint8 | None
    hc: np.uint8 | None
    frc: str

    @classmethod
    def from_str(cls, s: str):
        items = s.strip().split()

        num_items = len(items)
        it_items = iter(items)

        sv = next(it_items)
        cv_class = (
            CommonViewClass(next(it_items)) if num_items != TrackType.RAW else None
        )
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

        if num_items != TrackType.RAW:
            duration = Duration.from_total_nanoseconds(
                (np.float64(next(it_items)) * 1e9).astype(np.int64)
            )
        else:
            duration = None

        elevation = np.float64(next(it_items)) * 0.1
        azimuth = np.float64(next(it_items)) * 0.1

        data: TrackData
        iono: IonosphericData
        match num_items:
            case TrackType.WITH_IONO:
                data, iono = TrackData.parse_with_iono(it_items)
            case TrackType.WITHOUT_IONO:
                data, iono = TrackData.parse_without_iono(it_items)
            case TrackType.RAW:
                data, iono = TrackData.parse_raw(it_items)
            case _:
                raise ValueError("Invalid number of items")

        if num_items != TrackType.RAW:
            fr = np.uint8(next(it_items))
            hc = np.uint8(next(it_items))
        else:
            fr = None
            hc = None

        frc = next(it_items)

        # TODO: Process checksum
        if num_items != TrackType.RAW:
            _ = next(it_items)

        return cls(
            cv_class, epoch, duration, sv, elevation, azimuth, data, iono, fr, hc, frc
        )


def _parse_value(
    value: str, type: np.dtype, conv: np.float64 | None = None
) -> np.float64 | None:
    try:
        return type(value) * conv if conv else type(value)
    except ValueError:
        return None
