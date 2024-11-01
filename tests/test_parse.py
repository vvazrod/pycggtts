from pathlib import Path

from hifitime import Duration, Epoch, TimeScale

from pycggtts import CGGTTS, CommonViewClass, ReferenceTime, Track


def test_parse_track_without_iono():
    content = "G99 99 59568 001000 0780 099 0099 +9999999999 +99999       +1536   +181   26 999 9999 +999 9999 +999 00 00 L1C D3"
    track = Track.from_str(content)
    assert track is not None
    assert track.sv == "G99"
    assert track.cv_class == CommonViewClass.SINGLE
    assert track.duration == Duration.from_total_nanoseconds(int(780.0 * 1e9))
    assert track.iono is None
    assert track.elevation == 9.9
    assert track.azimuth == 9.9
    assert abs(track.data.dsg - 2.5e-9) < 1e-6
    assert abs(track.data.srsys - 2.83e-11) < 1e-6
    assert track.fr == 0
    assert track.hc == 0
    assert track.frc == "L1C"

    content = "G99 99 59563 001400 0780 099 0099 +9999999999 +99999       +1588  +1027   27 999 9999 +999 9999 +999 00 00 L1C EA"
    track = Track.from_str(content)
    assert track is not None
    assert track.sv == "G99"
    assert track.cv_class == CommonViewClass.SINGLE
    assert track.duration == Duration.from_total_nanoseconds(int(780.0 * 1e9))
    assert track.iono is None
    assert track.elevation == 9.9
    assert track.azimuth == 9.9
    assert track.fr == 0
    assert track.hc == 0
    assert track.frc == "L1C"

    content = "G99 99 59563 232200 0780 099 0099 +9999999999 +99999       +1529   -507   23 999 9999 +999 9999 +999 00 00 L1C D9"
    track = Track.from_str(content)
    assert track is not None
    assert track.sv == "G99"
    assert track.cv_class == CommonViewClass.SINGLE
    assert track.duration == Duration.from_total_nanoseconds(int(780.0 * 1e9))
    assert track.iono is None
    assert track.elevation == 9.9
    assert track.azimuth == 9.9
    assert track.fr == 0
    assert track.hc == 0
    assert track.frc == "L1C"

    content = "G99 99 59567 001400 0780 099 0099 +9999999999 +99999       +1561   -151   27 999 9999 +999 9999 +999 00 00 L1C D4"
    track = Track.from_str(content)
    assert track is not None
    assert track.sv == "G99"
    assert track.cv_class == CommonViewClass.SINGLE
    assert track.duration == Duration.from_total_nanoseconds(int(780.0 * 1e9))
    assert track.iono is None
    assert track.elevation == 9.9
    assert track.azimuth == 9.9
    assert track.fr == 0
    assert track.hc == 0
    assert track.frc == "L1C"


def test_parse_track_with_iono():
    content = "R24 FF 57000 000600 0780 347 0394 +1186342 +0 163 +0 40 2 141 +22 23 -1 23 -1 29 +2 0 L3P EF"
    track = Track.from_str(content)
    assert track is not None
    assert track.sv == "R24"
    assert track.cv_class == CommonViewClass.MULTI
    assert track.duration == Duration.from_total_nanoseconds(int(780.0 * 1e9))
    assert track.iono is not None
    assert track.iono.msio == 23.0e-10
    assert track.iono.smsi == -1.0e-13
    assert track.iono.isg == 29.0e-10
    assert track.elevation == 34.7
    assert abs(track.azimuth - 39.4) < 1e-6
    assert track.fr == 2
    assert track.hc == 0
    assert track.frc == "L3P"


def test_parse_gzsy8259_568():
    filepath = Path(__file__).parent / "../data" / "single" / "GZSY8259.568"
    cggtts = CGGTTS.from_file(filepath)
    assert cggtts is not None
    assert cggtts.release_date == Epoch.init_from_gregorian_at_midnight(
        2014, 2, 20, TimeScale.UTC
    )
    assert cggtts.receiver == "GORGYTIMING"
    assert cggtts.station == "SY82"
    assert cggtts.num_channels == 12
    assert cggtts.ims is None
    assert cggtts.reference_time == ReferenceTime.from_str("REF(SY82)")
    assert cggtts.reference_frame == "ITRF"
    assert abs(cggtts.apc_coordinates.x - 4314143.824) < 1e-6
    assert abs(cggtts.apc_coordinates.y - 452633.241) < 1e-6
    assert abs(cggtts.apc_coordinates.z - 4660711.385) < 1e-6
    assert cggtts.comments is None
    assert len(cggtts.tracks) == 32

    first_track = cggtts.tracks[0]
    assert first_track is not None
    assert first_track.sv == "G99"


def test_parse_ezug0060_600():
    filepath = Path(__file__).parent / "../data" / "dual" / "EZUG0060.600"
    cggtts = CGGTTS.from_file(filepath)
    assert cggtts is not None
    assert cggtts.release_date == Epoch.init_from_gregorian_at_midnight(
        2023, 7, 12, TimeScale.UTC
    )
    assert cggtts.receiver == "PolaRx5TR"
    assert cggtts.ims is None
    assert cggtts.station == "UGR"
    assert cggtts.num_channels == 80
    assert cggtts.apc_coordinates.x == 5077155.269
    assert cggtts.apc_coordinates.y == -321597.459
    assert cggtts.apc_coordinates.z == 3835335.920
    assert cggtts.comments is not None
    assert cggtts.delay.cab_delay == 157.0
    assert cggtts.delay.ref_delay == 5.0
    assert len(cggtts.tracks) == 634


def test_parse_raw():
    filepath = Path(__file__).parent / "../data" / "raw" / "CTTS_GAL_30s_E1"
    cggtts = CGGTTS.from_file(filepath)
    assert cggtts is not None
    assert cggtts.release_date is None
    assert cggtts.receiver is None
    assert cggtts.ims is None
    assert cggtts.station == "UGR"
    assert cggtts.num_channels == 0
    assert cggtts.apc_coordinates.x == 5077155.53
    assert cggtts.apc_coordinates.y == -321597.67
    assert cggtts.apc_coordinates.z == +3835335.89
    assert cggtts.comments is not None
    assert cggtts.delay.cab_delay == 157.0
    assert cggtts.delay.ref_delay == 5.0
    assert len(cggtts.tracks) == 79
