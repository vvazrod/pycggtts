from pycggtts.reftime import TAI, UTC, ReferenceTime


def test_from_str():
    assert isinstance(ReferenceTime.from_str("tai"), TAI)
    assert isinstance(ReferenceTime.from_str("utc"), UTC)
    assert ReferenceTime.from_str("UTC(LAB)") == ReferenceTime.from_str("UTC(LAB )")
