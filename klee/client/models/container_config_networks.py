from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.end_point_config import EndPointConfig


T = TypeVar("T", bound="ContainerConfigNetworks")


@attr.s(auto_attribs=True)
class ContainerConfigNetworks:
    """A mapping of network name to endpoint configuration for that network. The 'container' property is ignored in each
    endpoint config and the created container's id is used instead. Use a dummy-string like 'unused_name' for the
    'container' property since it is mandatory.

    """

    additional_properties: Dict[str, "EndPointConfig"] = attr.ib(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        pass

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.end_point_config import EndPointConfig

        d = src_dict.copy()
        container_config_networks = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = EndPointConfig.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        container_config_networks.additional_properties = additional_properties
        return container_config_networks

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "EndPointConfig":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "EndPointConfig") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
