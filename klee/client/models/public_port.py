from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.public_port_protocol import PublicPortProtocol

T = TypeVar("T", bound="PublicPort")


@_attrs_define
class PublicPort:
    """FIXME

    Attributes:
        container_port (str): port or portrange on the host that accepts traffic from `host_port`.
        host_port (str): source port or portrange on the host where incoming traffic is redirected
        interfaces (List[str]): List of host interfaces where `host_port` is going to be public, i.e., where traffic to
            the `host_port` is redirected to the container.
            If the list is empty, the hosts gateway interface is used.
        ip_address (str): ipv4 address within the container that receives traffic from the public port
        ip_address6 (str): ipv6 address within the container that receives traffic from the public port
        protocol (PublicPortProtocol): tcp or udp
    """

    container_port: str
    host_port: str
    interfaces: List[str]
    ip_address: str
    ip_address6: str
    protocol: PublicPortProtocol
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container_port = self.container_port
        host_port = self.host_port
        interfaces = self.interfaces

        ip_address = self.ip_address
        ip_address6 = self.ip_address6
        protocol = self.protocol.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "container_port": container_port,
                "host_port": host_port,
                "interfaces": interfaces,
                "ip_address": ip_address,
                "ip_address6": ip_address6,
                "protocol": protocol,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_port = d.pop("container_port")

        host_port = d.pop("host_port")

        interfaces = cast(List[str], d.pop("interfaces"))

        ip_address = d.pop("ip_address")

        ip_address6 = d.pop("ip_address6")

        protocol = PublicPortProtocol(d.pop("protocol"))

        public_port = cls(
            container_port=container_port,
            host_port=host_port,
            interfaces=interfaces,
            ip_address=ip_address,
            ip_address6=ip_address6,
            protocol=protocol,
        )

        public_port.additional_properties = d
        return public_port

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
