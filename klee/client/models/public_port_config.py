from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.public_port_config_protocol import PublicPortConfigProtocol
from ..types import UNSET, Unset

T = TypeVar("T", bound="PublicPortConfig")


@_attrs_define
class PublicPortConfig:
    """FIXME

    Attributes:
        container_port (int): port or portrange on the host that accepts traffic from `host_port`.
        host_port (int): source port or portrange on the host where incoming traffic is redirected
        interfaces (List[str]): List of host interfaces where the port is published, i.e., where traffic to the
            designated `host_port` is redirected to the container's ip4/ip6 addresses on the specified network. If the list
            is empty, the hosts gateway interface is used.
        protocol (Union[Unset, PublicPortConfigProtocol]): Whether to use TCP or UDP as transport protocol Default:
            PublicPortConfigProtocol.TCP.
    """

    container_port: int
    host_port: int
    interfaces: List[str]
    protocol: Union[Unset, PublicPortConfigProtocol] = PublicPortConfigProtocol.TCP
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container_port = self.container_port
        host_port = self.host_port
        interfaces = self.interfaces

        protocol: Union[Unset, str] = UNSET
        if not isinstance(self.protocol, Unset):
            protocol = self.protocol.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "container_port": container_port,
                "host_port": host_port,
                "interfaces": interfaces,
            }
        )
        if protocol is not UNSET:
            field_dict["protocol"] = protocol

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_port = d.pop("container_port")

        host_port = d.pop("host_port")

        interfaces = cast(List[str], d.pop("interfaces"))

        _protocol = d.pop("protocol", UNSET)
        protocol: Union[Unset, PublicPortConfigProtocol]
        if isinstance(_protocol, Unset):
            protocol = UNSET
        else:
            protocol = PublicPortConfigProtocol(_protocol)

        public_port_config = cls(
            container_port=container_port,
            host_port=host_port,
            interfaces=interfaces,
            protocol=protocol,
        )

        public_port_config.additional_properties = d
        return public_port_config

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
