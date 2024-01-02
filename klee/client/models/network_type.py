from enum import Enum


class NetworkType(str, Enum):
    BRIDGE = "bridge"
    CUSTOM = "custom"
    LOOPBACK = "loopback"

    def __str__(self) -> str:
        return str(self.value)
