from enum import Enum


class ContainerRestartPolicy(str, Enum):
    NO = "no"
    ON_STARTUP = "on-startup"

    def __str__(self) -> str:
        return str(self.value)
