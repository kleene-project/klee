from enum import Enum


class MountPointConfigType(str, Enum):
    NULLFS = "nullfs"
    VOLUME = "volume"

    def __str__(self) -> str:
        return str(self.value)
