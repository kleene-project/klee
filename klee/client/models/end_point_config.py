from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EndPointConfig")


@_attrs_define
class EndPointConfig:
    """Configuration of a connection between a network to a container.

    Attributes:
        container (str): Container identifier, i.e., the name, ID, or an initial unique segment of the ID.
        network (str): Network identifier, i.e., the name, ID, or an initial unique segment of the ID.
        ip_address (Union[Unset, str]): IPv4 address for the container. If set to `"<auto>"` an unused ip from the
            subnet will be used. If set to `""` no address will be set. Default: ''. Example: 10.13.37.33.
        ip_address6 (Union[Unset, str]): IPv6 address for the container. If set to `"<auto>"` an unused ip from the
            subnet will be used. If set to `""` no address will be set. Default: ''. Example: 2001:db8:8a2e:370:7334::2.
    """

    container: str
    network: str
    ip_address: Union[Unset, str] = ""
    ip_address6: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container = self.container
        network = self.network
        ip_address = self.ip_address
        ip_address6 = self.ip_address6

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "container": container,
                "network": network,
            }
        )
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if ip_address6 is not UNSET:
            field_dict["ip_address6"] = ip_address6

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container = d.pop("container")

        network = d.pop("network")

        ip_address = d.pop("ip_address", UNSET)

        ip_address6 = d.pop("ip_address6", UNSET)

        end_point_config = cls(
            container=container,
            network=network,
            ip_address=ip_address,
            ip_address6=ip_address6,
        )

        end_point_config.additional_properties = d
        return end_point_config

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
