from dataclasses import dataclass, field

import numpy as np

from .code import Code


@dataclass
class Delay:
    """GNSS receiver delay.

    Delays are always specified in nanoseconds.
    """

    value: np.float64

    def __format__(self, format_spec):
        return f"{self.delay}"

    @property
    def value_seconds(self):
        return self.value * 1e-9

    def add_value(self, rhs):
        self.value += rhs


@dataclass
class SystemDelay:
    """Describes the total measurement system's delay."""

    cab_delay: np.float64 = 0.0
    ref_delay: np.float64 = 0.0
    delays: dict[Code, Delay] = field(default_factory=dict)
    cal_id: str | None = None

    def total_delay(self, code: Code) -> np.float64 | None:
        """Return the total delay for a given code."""

        if code not in self.delays:
            return None

        return self.cab_delay + self.ref_delay + self.delays[code].value

    def total_delays(self) -> list[tuple[Code, np.float64]]:
        """Group the total delays for each code."""

        return [(code, self.total_delay(code)) for code in self.delays.keys()]
