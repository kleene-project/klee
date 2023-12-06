from enum import Enum


class MountPointType(str, Enum):
    NULLFS = "nullfs"
    VOLUME = "volume"

    def __str__(self) -> str:
        return str(self.value)
