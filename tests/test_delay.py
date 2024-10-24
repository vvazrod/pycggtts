from pycggtts import Code, Delay, DelayKind, SystemDelay


def test_delay():
    delay = Delay(DelayKind.INTERNAL, 10.0)
    assert delay.kind == DelayKind.INTERNAL
    assert delay.value == 10.0
    assert delay.value_seconds == 10.0e-9
    assert delay == Delay(DelayKind.INTERNAL, 10.0)
    delay.add_value(20.0)
    assert delay == Delay(DelayKind.INTERNAL, 30.0)
    delay = Delay(DelayKind.SYSTEM, 25.5)
    assert delay.kind == DelayKind.SYSTEM
    assert delay.value == 25.5
    assert delay.value_seconds == 25.5e-9
    assert delay == Delay(DelayKind.SYSTEM, 25.5)
    delay.add_value(30.0)
    assert delay == Delay(DelayKind.SYSTEM, 55.5)


def test_system_delay():
    delay = SystemDelay()
    assert delay.rf_cable_delay == 0.0
    assert delay.ref_delay == 0.0
    delay.rf_cable_delay = 10.0
    delay.ref_delay = 20.0
    delay.delays.update({Code.C1: Delay(DelayKind.INTERNAL, 50.0)})
    assert delay.rf_cable_delay == 10.0
    assert delay.ref_delay == 20.0
    total = delay.total_delay(Code.C1)
    assert total
    assert total == 80.0
    totals = delay.total_delays()
    assert len(totals) > 0
    assert totals[0][0] == Code.C1
    assert totals[0][1] == 80.0
    assert delay.total_delay(Code.C2) is None
