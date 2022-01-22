from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkConfig")


@attr.s(auto_attribs=True)
class NetworkConfig:
    """Network configuration

    Attributes:
        ifname (str): Name of the interface that is being used for the network. Example: jocker0.
        name (str): Name of the network. Example: westnet.
        subnet (str): The subnet (in CIDR-format) that is used for the network. Example: 10.13.37.0/24.
        driver (Union[Unset, str]): Network type. Only 'loopback' type of network is supported. Example: loopback.
    """

    ifname: str
    name: str
    subnet: str
    driver: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ifname = self.ifname
        name = self.name
        subnet = self.subnet
        driver = self.driver

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ifname": ifname,
                "name": name,
                "subnet": subnet,
            }
        )
        if driver is not UNSET:
            field_dict["driver"] = driver

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ifname = d.pop("ifname")

        name = d.pop("name")

        subnet = d.pop("subnet")

        driver = d.pop("driver", UNSET)

        network_config = cls(
            ifname=ifname,
            name=name,
            subnet=subnet,
            driver=driver,
        )

        network_config.additional_properties = d
        return network_config

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
