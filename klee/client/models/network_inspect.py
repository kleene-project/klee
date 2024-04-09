from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.end_point import EndPoint
    from ..models.network import Network


T = TypeVar("T", bound="NetworkInspect")


@_attrs_define
class NetworkInspect:
    """Detailed information on a network.

    Attributes:
        network (Union[Unset, Network]): Kleene network
        network_endpoints (Union[Unset, List['EndPoint']]): Endpoints of the network.
    """

    network: Union[Unset, "Network"] = UNSET
    network_endpoints: Union[Unset, List["EndPoint"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        network: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.network, Unset):
            network = self.network.to_dict()

        network_endpoints: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.network_endpoints, Unset):
            network_endpoints = []
            for network_endpoints_item_data in self.network_endpoints:
                network_endpoints_item = network_endpoints_item_data.to_dict()

                network_endpoints.append(network_endpoints_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if network is not UNSET:
            field_dict["network"] = network
        if network_endpoints is not UNSET:
            field_dict["network_endpoints"] = network_endpoints

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.end_point import EndPoint
        from ..models.network import Network

        d = src_dict.copy()
        _network = d.pop("network", UNSET)
        network: Union[Unset, Network]
        if isinstance(_network, Unset):
            network = UNSET
        else:
            network = Network.from_dict(_network)

        network_endpoints = []
        _network_endpoints = d.pop("network_endpoints", UNSET)
        for network_endpoints_item_data in _network_endpoints or []:
            network_endpoints_item = EndPoint.from_dict(network_endpoints_item_data)

            network_endpoints.append(network_endpoints_item)

        network_inspect = cls(
            network=network,
            network_endpoints=network_endpoints,
        )

        network_inspect.additional_properties = d
        return network_inspect

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
