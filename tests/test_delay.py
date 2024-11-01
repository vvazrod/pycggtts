from pycggtts import Code, Delay, SystemDelay


def test_delay():
    delay = Delay(10.0)
    assert delay.value == 10.0
    assert delay.value_seconds == 10.0e-9
    assert delay == Delay(10.0)
    delay.add_value(20.0)
    assert delay == Delay(30.0)


def test_system_delay():
    delay = SystemDelay()
    assert delay.cab_delay == 0.0
    assert delay.ref_delay == 0.0
    delay.cab_delay = 10.0
    delay.ref_delay = 20.0
    delay.delays.update({Code.C1: Delay(50.0)})
    assert delay.cab_delay == 10.0
    assert delay.ref_delay == 20.0
    total = delay.total_delay(Code.C1)
    assert total
    assert total == 80.0
    totals = delay.total_delays()
    assert len(totals) > 0
    assert totals[0][0] == Code.C1
    assert totals[0][1] == 80.0
    assert delay.total_delay(Code.C2) is None
