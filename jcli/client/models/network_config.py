from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkConfig")


@attr.s(auto_attribs=True)
class NetworkConfig:
    """Network configuration

    Attributes:
        name (str): Name of the network. Example: westnet.
        driver (Union[Unset, str]): Network type. Only 'loopback' type of network is supported. Example: loopback.
        ifname (Union[Unset, str]): Name of the interface that is being used for the network. Example: jocker0.
        subnet (Union[Unset, str]): The subnet (in CIDR-format) that is used for the network. Example: 10.13.37.0/24.
    """

    name: str
    driver: Union[Unset, str] = UNSET
    ifname: Union[Unset, str] = UNSET
    subnet: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        driver = self.driver
        ifname = self.ifname
        subnet = self.subnet

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if driver is not UNSET:
            field_dict["driver"] = driver
        if ifname is not UNSET:
            field_dict["ifname"] = ifname
        if subnet is not UNSET:
            field_dict["subnet"] = subnet

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        driver = d.pop("driver", UNSET)

        ifname = d.pop("ifname", UNSET)

        subnet = d.pop("subnet", UNSET)

        network_config = cls(
            name=name,
            driver=driver,
            ifname=ifname,
            subnet=subnet,
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
