import re
from dataclasses import dataclass


@dataclass
class TAI:
    """International Atomic Time."""

    pass


@dataclass
class UTC:
    """Coordinated Universal Time."""

    pass


@dataclass
class UTCk:
    """Coordinated Universal Time laboratory realization."""

    lab: str


@dataclass
class Custom:
    """Custom reference time system."""

    s: str


ReferenceTimeUnion = TAI | UTC | UTCk | Custom


class ReferenceTime:
    """Reference time system."""

    _system: ReferenceTimeUnion

    def __init__(self, system: ReferenceTimeUnion):
        self._system = system

    def __str__(self):
        match self._system:
            case TAI():
                return "TAI"
            case UTC():
                return "UTC"
            case UTCk(lab):
                return f"UTC({lab})"
            case Custom(s):
                return s

    def __eq__(self, other):
        print(other.__class__)
        print(self.__class__)
        if not isinstance(other, ReferenceTime):
            return False

        print(self)
        if self._system.__class__ == other._system.__class__:
            print(self._system)
            match self._system:
                case UTCk(lab):
                    return lab == other._system.lab
                case Custom(s):
                    return s == other._system.s
                case _:
                    return True

        return False

    @classmethod
    def from_str(cls, s: str):
        if s == "tai":
            return TAI()
        elif s == "utc":
            return UTC()
        elif (lab := re.search(r"UTC\((\s*\w+\s*)\)", s)) is not None:
            return UTCk(lab.group(1).strip())
        else:
            return Custom(s)
