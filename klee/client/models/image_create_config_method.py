from enum import Enum


class ImageCreateConfigMethod(str, Enum):
    FETCH = "fetch"
    ZFS = "zfs"

    def __str__(self) -> str:
        return str(self.value)
