from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.network_config_type import NetworkConfigType
from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkConfig")


@_attrs_define
class NetworkConfig:
    """Network configuration

    Attributes:
        name (str): Name of the network. Example: westnet.
        type (NetworkConfigType): What kind of network should be created. Example: bridge.
        gateway (Union[Unset, str]): **`bridge` networks only**

            The default (IPv4) router that is added to `vnet` containers connecting to bridged networks.
            If set to `""` no gateway is used. If set to `"<auto>"` the first IP of the subnet is added to `interface` and
            used as gateway.
             Default: ''. Example: 192.168.1.1.
        gateway6 (Union[Unset, str]): **`bridge` networks only**

            The default IPv6 router that is added to `vnet` containers connecting to bridged networks.
            See `gateway` for details.
             Default: ''. Example: 2001:db8:8a2e:370:7334::1.
        icc (Union[Unset, bool]): Inter-container connectvity: Whether or not to enable connectivity between containers
            within the same network. Default: True.
        interface (Union[Unset, str]): Name of the host interface used for the network.
            If set to `""` the name is set to `kleened` postfixed with an integer.
            If `type` is set to `custom` the value of `interface` must refer to an existing interface,
            otherwise it is created by Kleened.
             Default: ''. Example: kleene0.
        internal (Union[Unset, bool]): Whether or not outgoing traffic is allowed on the network.
        nat (Union[Unset, str]): Interface used for NAT'ing outgoing traffic from the network.
            If set to `"<host-gateway>"` the hosts gateway interface is used, if it exists.
            If set to `""` no NAT'ing is configured.
             Default: '<host-gateway>'. Example: igb0.
        subnet (Union[Unset, str]): The IPv4 subnet (in CIDR-format) that is used for the network. If set to `""` no
            IPv4 subnet is used. Default: ''. Example: 10.13.37.0/24.
        subnet6 (Union[Unset, str]): The IPv6 subnet (in CIDR-format) that is used for the network. If set to `""` no
            IPv6 subnet is used. Default: ''. Example: 2001:db8:8a2e:370:7334::/64.
    """

    name: str
    type: NetworkConfigType
    gateway: Union[Unset, str] = ""
    gateway6: Union[Unset, str] = ""
    icc: Union[Unset, bool] = True
    interface: Union[Unset, str] = ""
    internal: Union[Unset, bool] = False
    nat: Union[Unset, str] = "<host-gateway>"
    subnet: Union[Unset, str] = ""
    subnet6: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        type = self.type.value

        gateway = self.gateway
        gateway6 = self.gateway6
        icc = self.icc
        interface = self.interface
        internal = self.internal
        nat = self.nat
        subnet = self.subnet
        subnet6 = self.subnet6

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type,
            }
        )
        if gateway is not UNSET:
            field_dict["gateway"] = gateway
        if gateway6 is not UNSET:
            field_dict["gateway6"] = gateway6
        if icc is not UNSET:
            field_dict["icc"] = icc
        if interface is not UNSET:
            field_dict["interface"] = interface
        if internal is not UNSET:
            field_dict["internal"] = internal
        if nat is not UNSET:
            field_dict["nat"] = nat
        if subnet is not UNSET:
            field_dict["subnet"] = subnet
        if subnet6 is not UNSET:
            field_dict["subnet6"] = subnet6

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type = NetworkConfigType(d.pop("type"))

        gateway = d.pop("gateway", UNSET)

        gateway6 = d.pop("gateway6", UNSET)

        icc = d.pop("icc", UNSET)

        interface = d.pop("interface", UNSET)

        internal = d.pop("internal", UNSET)

        nat = d.pop("nat", UNSET)

        subnet = d.pop("subnet", UNSET)

        subnet6 = d.pop("subnet6", UNSET)

        network_config = cls(
            name=name,
            type=type,
            gateway=gateway,
            gateway6=gateway6,
            icc=icc,
            interface=interface,
            internal=internal,
            nat=nat,
            subnet=subnet,
            subnet6=subnet6,
        )

        network_config.additional_properties = d
        return network_config

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
