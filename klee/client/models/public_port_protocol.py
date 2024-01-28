from enum import Enum


class PublicPortProtocol(str, Enum):
    TCP = "tcp"
    UDP = "udp"

    def __str__(self) -> str:
        return str(self.value)
