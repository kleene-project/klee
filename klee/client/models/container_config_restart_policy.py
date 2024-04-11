from enum import Enum


class ContainerConfigRestartPolicy(str, Enum):
    NO = "no"
    ON_STARTUP = "on-startup"

    def __str__(self) -> str:
        return str(self.value)
