from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EndPoint")


@_attrs_define
class EndPoint:
    """Endpoint connecting a container to a network.

    Attributes:
        container_id (Union[Unset, str]): ID of the container that this endpoint belongs to.
        epair (Union[Unset, None, str]): **`vnet` containers only**

            `epair(4)` interfaces connecting the container to the network.
        id (Union[Unset, str]): Endpoint ID
        ip_address (Union[Unset, str]): The IPv4 address of the container. Example: 10.13.37.33.
        ip_address6 (Union[Unset, str]): The IPv6 address of the container. Example: 2610:1c1:1:606c::50:15.
        network_id (Union[Unset, str]): Name of the network that this endpoint belongs to.
    """

    container_id: Union[Unset, str] = UNSET
    epair: Union[Unset, None, str] = UNSET
    id: Union[Unset, str] = UNSET
    ip_address: Union[Unset, str] = UNSET
    ip_address6: Union[Unset, str] = UNSET
    network_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container_id = self.container_id
        epair = self.epair
        id = self.id
        ip_address = self.ip_address
        ip_address6 = self.ip_address6
        network_id = self.network_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container_id is not UNSET:
            field_dict["container_id"] = container_id
        if epair is not UNSET:
            field_dict["epair"] = epair
        if id is not UNSET:
            field_dict["id"] = id
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if ip_address6 is not UNSET:
            field_dict["ip_address6"] = ip_address6
        if network_id is not UNSET:
            field_dict["network_id"] = network_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_id = d.pop("container_id", UNSET)

        epair = d.pop("epair", UNSET)

        id = d.pop("id", UNSET)

        ip_address = d.pop("ip_address", UNSET)

        ip_address6 = d.pop("ip_address6", UNSET)

        network_id = d.pop("network_id", UNSET)

        end_point = cls(
            container_id=container_id,
            epair=epair,
            id=id,
            ip_address=ip_address,
            ip_address6=ip_address6,
            network_id=network_id,
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
