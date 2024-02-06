from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ImageBuildargs")


@_attrs_define
class ImageBuildargs:
    """Object of string pairs for build-time variables. Users pass these values at build-time. Kleened uses the buildargs
    as the environment context for commands run via the Dockerfile RUN instruction, or for variable expansion in other
    Dockerfile instructions. This is not meant for passing secret values.

        Example:
            {'JAIL_MGMT_ENGINE': 'kleene', 'USERNAME': 'Stephen'}

    """

    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        image_buildargs = cls()

        image_buildargs.additional_properties = d
        return image_buildargs

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
