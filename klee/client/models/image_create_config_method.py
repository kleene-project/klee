from enum import Enum


class ImageCreateConfigMethod(str, Enum):
    FETCH = "fetch"
    FETCH_AUTO = "fetch-auto"
    ZFS_CLONE = "zfs-clone"
    ZFS_COPY = "zfs-copy"

    def __str__(self) -> str:
        return str(self.value)
