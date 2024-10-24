from enum import Enum, auto


class NonSupportedVersionError(Exception):
    """Raised when the version is not supported."""

    pass


class Version(Enum):
    VERSION_2E = auto()

    @classmethod
    def from_str(cls, version: str):
        if version == "2E":
            return cls.VERSION_2E
        else:
            raise NonSupportedVersionError(f"Version {version} is not supported.")
