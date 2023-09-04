from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="EndPointConfig")


@attr.s(auto_attribs=True)
class EndPointConfig:
    """Configuration of a connection between a network to a container.

    Attributes:
        container (str): Name or (possibly truncated) id of the container
        ip_address (Union[Unset, str]): The ip(v4) address that should be assigned to the container. If this field is
            not set (or null) an unused ip contained in the subnet is auto-generated. Example: 10.13.37.33.
    """

    container: str
    ip_address: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container = self.container
        ip_address = self.ip_address

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "container": container,
            }
        )
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container = d.pop("container")

        ip_address = d.pop("ip_address", UNSET)

        end_point_config = cls(
            container=container,
            ip_address=ip_address,
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
