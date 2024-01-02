from enum import Enum


class NetworkConfigType(str, Enum):
    BRIDGE = "bridge"
    CUSTOM = "custom"
    LOOPBACK = "loopback"

    def __str__(self) -> str:
        return str(self.value)
