from enum import Enum, auto


class NonSupportedVersionError(Exception):
    """Raised when the version is not supported."""

    pass


class Version(Enum):
    """Supported versions of the CGGTTS format.

    Currently, only version 2E (latest) is supported. We also support reading 30s raw
    data generated by programs like R2CGGTTS.
    """

    VERSION_2E = auto()
    RAW = auto()

    @classmethod
    def from_str(cls, version: str):
        if version == "2E":
            return cls.VERSION_2E
        else:
            raise NonSupportedVersionError(f"Version {version} is not supported.")
