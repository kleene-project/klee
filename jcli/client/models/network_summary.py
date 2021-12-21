from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkSummary")


@attr.s(auto_attribs=True)
class NetworkSummary:
    """summary description of a network

    Attributes:
        default_gw_if (Union[Unset, bool]): interface where the gateway can be reached
        driver (Union[Unset, str]): Which type of network is used. Possible values are 'loopback' where the network is
            situated on a loopback interface on the host, and 'host' where the container have inherited the hosts network
            configuration. Only one read-only network exists with the 'host' driver.
        id (Union[Unset, str]): The id of the network
        if_name (Union[Unset, str]): Name of the loopback interface used for the network
        name (Union[Unset, str]): Name of the network
        subnet (Union[Unset, str]): Subnet used for the network
    """

    default_gw_if: Union[Unset, bool] = UNSET
    driver: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    if_name: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    subnet: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        default_gw_if = self.default_gw_if
        driver = self.driver
        id = self.id
        if_name = self.if_name
        name = self.name
        subnet = self.subnet

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_gw_if is not UNSET:
            field_dict["default_gw_if"] = default_gw_if
        if driver is not UNSET:
            field_dict["driver"] = driver
        if id is not UNSET:
            field_dict["id"] = id
        if if_name is not UNSET:
            field_dict["if_name"] = if_name
        if name is not UNSET:
            field_dict["name"] = name
        if subnet is not UNSET:
            field_dict["subnet"] = subnet

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        default_gw_if = d.pop("default_gw_if", UNSET)

        driver = d.pop("driver", UNSET)

        id = d.pop("id", UNSET)

        if_name = d.pop("if_name", UNSET)

        name = d.pop("name", UNSET)

        subnet = d.pop("subnet", UNSET)

        network_summary = cls(
            default_gw_if=default_gw_if,
            driver=driver,
            id=id,
            if_name=if_name,
            name=name,
            subnet=subnet,
        )

        network_summary.additional_properties = d
        return network_summary

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
