from enum import Enum


class WebSocketMessageMsgType(str, Enum):
    CLOSING = "closing"
    ERROR = "error"
    STARTING = "starting"

    def __str__(self) -> str:
        return str(self.value)
