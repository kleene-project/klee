from enum import Enum


class DeploymentServiceConfigNetworkDriver(str, Enum):
    DISABLED = "disabled"
    HOST = "host"
    IPNET = "ipnet"
    VNET = "vnet"

    def __str__(self) -> str:
        return str(self.value)
