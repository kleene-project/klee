from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.published_port_config_protocol import PublishedPortConfigProtocol
from ..types import UNSET, Unset

T = TypeVar("T", bound="PublishedPortConfig")


@_attrs_define
class PublishedPortConfig:
    """Configuration for publishing a port of a container.

    Attributes:
        container_port (str): Destination port (or portrange) of the container that accepts traffic from `host_port`.

            `container_port` can take two forms, depending on `host_port`:
            - A single portnumber `"PORTNUMBER"` if `host_port` is a single port number
            - A portrange `"PORTNUMBER_START:*"` if `host_port` is a port range
        host_port (str): Source port (or portrange) on the host where incoming traffic is redirected.

            `host_port` can take one of two forms:
            - A single portnumber `"PORTNUMBER"`
            - A portrange `"PORTNUMBER_START:PORTNUMBER_END"`
        interfaces (List[str]): List of host interfaces where the port is published, i.e.,
            where traffic to `host_port` is redirected to `container_port` (on a random IP-address).
            If set to `[]` the host's gateway interface is used.
        protocol (Union[Unset, PublishedPortConfigProtocol]): Whether to use TCP or UDP as transport protocol Default:
            PublishedPortConfigProtocol.TCP.
    """

    container_port: str
    host_port: str
    interfaces: List[str]
    protocol: Union[Unset, PublishedPortConfigProtocol] = (
        PublishedPortConfigProtocol.TCP
    )
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
        protocol: Union[Unset, PublishedPortConfigProtocol]
        if isinstance(_protocol, Unset):
            protocol = UNSET
        else:
            protocol = PublishedPortConfigProtocol(_protocol)

        published_port_config = cls(
            container_port=container_port,
            host_port=host_port,
            interfaces=interfaces,
            protocol=protocol,
        )

        published_port_config.additional_properties = d
        return published_port_config

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
