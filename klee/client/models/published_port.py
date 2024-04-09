from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.published_port_protocol import PublishedPortProtocol

T = TypeVar("T", bound="PublishedPort")


@_attrs_define
class PublishedPort:
    """A published port of a container, i.e., opening up the port for incoming traffic from external sources.

    Attributes:
        container_port (str): Destination port (or portrange) of the container that accepts traffic from `host_port`.

            `container_port` can take two forms, depending on `host_port`:
            - A single portnumber `"PORTNUMBER"` if `host_port` is a single port number
            - A portrange `"PORTNUMBER_START:*"` if `host_port` is a port range
        host_port (str): Source port (or portrange) on the host where incoming traffic is redirected.

            `host_port` can take one of two forms:
            - A single portnumber `"PORTNUMBER"`
            - A portrange `"PORTNUMBER_START:PORTNUMBER_END"`
        interfaces (List[str]): List of host interfaces where incoming traffic to `host_port` is redirected to the
            container at `ip_address` and/or `ip_address6` on `container_port`.
        ip_address (str): ipv4 address within the container that receives traffic to `container_port`
        ip_address6 (str): ipv6 address within the container that receives traffic to `container_port`
        protocol (PublishedPortProtocol): tcp or udp
    """

    container_port: str
    host_port: str
    interfaces: List[str]
    ip_address: str
    ip_address6: str
    protocol: PublishedPortProtocol
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

        protocol = PublishedPortProtocol(d.pop("protocol"))

        published_port = cls(
            container_port=container_port,
            host_port=host_port,
            interfaces=interfaces,
            ip_address=ip_address,
            ip_address6=ip_address6,
            protocol=protocol,
        )

        published_port.additional_properties = d
        return published_port

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
