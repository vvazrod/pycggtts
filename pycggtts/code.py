from enum import StrEnum, auto


class Code(StrEnum):
    """GNSS code types."""

    C1 = auto()
    C2 = auto()
    P1 = auto()
    P2 = auto()
    E1 = auto()
    E5 = auto()
    B1 = auto()
    B2 = auto()
