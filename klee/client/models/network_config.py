from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkConfig")


@attr.s(auto_attribs=True)
class NetworkConfig:
    """Network configuration

    Attributes:
        driver (str): Which driver to use for the network. Possible values are 'vnet', 'loopback', and 'host'.
            See jails(8) and the networking documentation for details.
             Example: vnet.
        name (str): Name of the network. Example: westnet.
        subnet (str): The subnet (in CIDR-format) that is used for the network. Example: 10.13.37.0/24.
        ifname (Union[Unset, str]): Name of the loopback interface that is being used for the network. Only used with
            the 'loopback' driver. Example: kleene0.
    """

    driver: str
    name: str
    subnet: str
    ifname: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        driver = self.driver
        name = self.name
        subnet = self.subnet
        ifname = self.ifname

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "driver": driver,
                "name": name,
                "subnet": subnet,
            }
        )
        if ifname is not UNSET:
            field_dict["ifname"] = ifname

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        driver = d.pop("driver")

        name = d.pop("name")

        subnet = d.pop("subnet")

        ifname = d.pop("ifname", UNSET)

        network_config = cls(
            driver=driver,
            name=name,
            subnet=subnet,
            ifname=ifname,
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
