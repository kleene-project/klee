from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImagePullConfig")


@_attrs_define
class ImagePullConfig:
    """Configuration for pulling an image from an OCI registry.

    Attributes:
        ref (str): Image reference to pull: `[registry/]repository[:tag][@digest]`.
            Unqualified names resolve against the configured default registry
            (`nginx` -> `docker.io/library/nginx`).
        platform (Union[Unset, None, str]): `os/architecture` selector when the registry serves a multi-platform
            index (e.g. `freebsd/amd64`). Defaults to the host's own
            os/architecture (from `uname(1)`).
    """

    ref: str
    platform: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref = self.ref
        platform = self.platform

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref": ref,
            }
        )
        if platform is not UNSET:
            field_dict["platform"] = platform

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref = d.pop("ref")

        platform = d.pop("platform", UNSET)

        image_pull_config = cls(
            ref=ref,
            platform=platform,
        )

        image_pull_config.additional_properties = d
        return image_pull_config

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
