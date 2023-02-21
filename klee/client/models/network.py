from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Network")


@attr.s(auto_attribs=True)
class Network:
    """summary description of a network

    Attributes:
        bridge_if (Union[Unset, str]): Name of the bridge interface (used for a 'vnet' network). Default: ''.
        driver (Union[Unset, str]): Type of network.
        id (Union[Unset, str]): The id of the network
        loopback_if (Union[Unset, str]): Name of the loopback interface (used for a 'loopback' network). Default: ''.
        name (Union[Unset, str]): Name of the network
        subnet (Union[Unset, str]): Subnet used for the network
    """

    bridge_if: Union[Unset, str] = ""
    driver: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    loopback_if: Union[Unset, str] = ""
    name: Union[Unset, str] = UNSET
    subnet: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bridge_if = self.bridge_if
        driver = self.driver
        id = self.id
        loopback_if = self.loopback_if
        name = self.name
        subnet = self.subnet

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bridge_if is not UNSET:
            field_dict["bridge_if"] = bridge_if
        if driver is not UNSET:
            field_dict["driver"] = driver
        if id is not UNSET:
            field_dict["id"] = id
        if loopback_if is not UNSET:
            field_dict["loopback_if"] = loopback_if
        if name is not UNSET:
            field_dict["name"] = name
        if subnet is not UNSET:
            field_dict["subnet"] = subnet

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bridge_if = d.pop("bridge_if", UNSET)

        driver = d.pop("driver", UNSET)

        id = d.pop("id", UNSET)

        loopback_if = d.pop("loopback_if", UNSET)

        name = d.pop("name", UNSET)

        subnet = d.pop("subnet", UNSET)

        network = cls(
            bridge_if=bridge_if,
            driver=driver,
            id=id,
            loopback_if=loopback_if,
            name=name,
            subnet=subnet,
        )

        network.additional_properties = d
        return network

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
