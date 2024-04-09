from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.network_type import NetworkType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Network")


@_attrs_define
class Network:
    """Kleene network

    Attributes:
        gateway (Union[Unset, str]): The default IPv4 router that is added to `vnet` containers connecting to the
            network.
            If `""` no gateway is used.
             Default: ''. Example: 192.168.1.1.
        gateway6 (Union[Unset, str]): The default IPv6 router that is added to 'vnet' containers connecting to the
            network.
            If `""` no gateway is used.
             Default: ''. Example: 2001:db8:8a2e:370:7334::1.
        icc (Union[Unset, bool]): Inter-container connectvity: Whether or not to enable connectivity between containers
            within the network. Default: True.
        id (Union[Unset, str]): ID of the network
        interface (Union[Unset, str]): Name for the interface that is being used for the network.
             Default: ''. Example: kleene0.
        internal (Union[Unset, bool]): Whether or not outgoing traffic is allowed on the network. Default: True.
        name (Union[Unset, str]): Name of the network. Example: westnet.
        nat (Union[Unset, str]): Which interface should be used for NAT'ing outgoing traffic from the network.
            If set to `""` no NAT'ing is configured.
             Default: ''. Example: igb0.
        subnet (Union[Unset, str]): The IPv4 subnet (in CIDR-format) that is used for the network. Example:
            10.13.37.0/24.
        subnet6 (Union[Unset, str]): The IPv6 subnet (in CIDR-format) that is used for the network. Example:
            2001:db8:8a2e:370:7334::/64.
        type (Union[Unset, NetworkType]): Network type. Example: bridge.
    """

    gateway: Union[Unset, str] = ""
    gateway6: Union[Unset, str] = ""
    icc: Union[Unset, bool] = True
    id: Union[Unset, str] = UNSET
    interface: Union[Unset, str] = ""
    internal: Union[Unset, bool] = True
    name: Union[Unset, str] = UNSET
    nat: Union[Unset, str] = ""
    subnet: Union[Unset, str] = UNSET
    subnet6: Union[Unset, str] = UNSET
    type: Union[Unset, NetworkType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        gateway = self.gateway
        gateway6 = self.gateway6
        icc = self.icc
        id = self.id
        interface = self.interface
        internal = self.internal
        name = self.name
        nat = self.nat
        subnet = self.subnet
        subnet6 = self.subnet6
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if gateway is not UNSET:
            field_dict["gateway"] = gateway
        if gateway6 is not UNSET:
            field_dict["gateway6"] = gateway6
        if icc is not UNSET:
            field_dict["icc"] = icc
        if id is not UNSET:
            field_dict["id"] = id
        if interface is not UNSET:
            field_dict["interface"] = interface
        if internal is not UNSET:
            field_dict["internal"] = internal
        if name is not UNSET:
            field_dict["name"] = name
        if nat is not UNSET:
            field_dict["nat"] = nat
        if subnet is not UNSET:
            field_dict["subnet"] = subnet
        if subnet6 is not UNSET:
            field_dict["subnet6"] = subnet6
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        gateway = d.pop("gateway", UNSET)

        gateway6 = d.pop("gateway6", UNSET)

        icc = d.pop("icc", UNSET)

        id = d.pop("id", UNSET)

        interface = d.pop("interface", UNSET)

        internal = d.pop("internal", UNSET)

        name = d.pop("name", UNSET)

        nat = d.pop("nat", UNSET)

        subnet = d.pop("subnet", UNSET)

        subnet6 = d.pop("subnet6", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, NetworkType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = NetworkType(_type)

        network = cls(
            gateway=gateway,
            gateway6=gateway6,
            icc=icc,
            id=id,
            interface=interface,
            internal=internal,
            name=name,
            nat=nat,
            subnet=subnet,
            subnet6=subnet6,
            type=type,
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
