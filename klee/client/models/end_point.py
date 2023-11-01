from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EndPoint")


@_attrs_define
class EndPoint:
    """Endpoint connecting a container to a network.

    Attributes:
        container (Union[Unset, str]): ID of the container that this endpoint belongs to.
        epair (Union[Unset, None, str]): epair used for endpoint in case of a VNET network
        id (Union[Unset, str]): EndPoint ID
        ip_address (Union[Unset, None, str]): IP address of the container connected to the network
        network (Union[Unset, str]): Name of the network that this endpoint belongs to.
    """

    container: Union[Unset, str] = UNSET
    epair: Union[Unset, None, str] = UNSET
    id: Union[Unset, str] = UNSET
    ip_address: Union[Unset, None, str] = UNSET
    network: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container = self.container
        epair = self.epair
        id = self.id
        ip_address = self.ip_address
        network = self.network

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container is not UNSET:
            field_dict["container"] = container
        if epair is not UNSET:
            field_dict["epair"] = epair
        if id is not UNSET:
            field_dict["id"] = id
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if network is not UNSET:
            field_dict["network"] = network

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container = d.pop("container", UNSET)

        epair = d.pop("epair", UNSET)

        id = d.pop("id", UNSET)

        ip_address = d.pop("ip_address", UNSET)

        network = d.pop("network", UNSET)

        end_point = cls(
            container=container,
            epair=epair,
            id=id,
            ip_address=ip_address,
            network=network,
        )

        end_point.additional_properties = d
        return end_point

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
