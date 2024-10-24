from dataclasses import dataclass

import numpy as np


@dataclass
class Receiver:
    """A GNSS receiver."""

    manufacturer: str
    model: str
    serial_number: str
    year: np.uint16
    release: str

    def __format__(self, format_spec):
        return f"{self.manufacturer} {self.model} {self.serial_number} {self.year} {self.release}"
