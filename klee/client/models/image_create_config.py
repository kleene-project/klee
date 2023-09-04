from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.image_create_config_method import ImageCreateConfigMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageCreateConfig")


@attr.s(auto_attribs=True)
class ImageCreateConfig:
    """Configuration for the creation of base images.

    Attributes:
        method (ImageCreateConfigMethod): Method used for creating a new base image: If 'fetch' is selected, kleened
            will fetch a release/snapshot of the base system and use it for image creation. When 'zfs' is used, a copy of
            the supplied zfs dataset is used for the image.
        force (Union[Unset, bool]): Ignore any discrepancies detected when using uname(1) to fetch the base system
            (method 'fetch' only).
        tag (Union[Unset, str]): Name and optionally a tag in the 'name:tag' format Default: ''.
        url (Union[Unset, str]): URL to a remote location where the base system (as a base.txz file) is stored. If an
            empty string is supplied kleened will try to fetch a version of the base sytem from download.freebsd.org using
            information from uname(1) (required for method 'fetch'). Default: ''.
        zfs_dataset (Union[Unset, str]): Dataset path on the host used for the image (required for method 'zfs' only).
            Default: ''.
    """

    method: ImageCreateConfigMethod
    force: Union[Unset, bool] = False
    tag: Union[Unset, str] = ""
    url: Union[Unset, str] = ""
    zfs_dataset: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        method = self.method.value

        force = self.force
        tag = self.tag
        url = self.url
        zfs_dataset = self.zfs_dataset

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "method": method,
            }
        )
        if force is not UNSET:
            field_dict["force"] = force
        if tag is not UNSET:
            field_dict["tag"] = tag
        if url is not UNSET:
            field_dict["url"] = url
        if zfs_dataset is not UNSET:
            field_dict["zfs_dataset"] = zfs_dataset

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        method = ImageCreateConfigMethod(d.pop("method"))

        force = d.pop("force", UNSET)

        tag = d.pop("tag", UNSET)

        url = d.pop("url", UNSET)

        zfs_dataset = d.pop("zfs_dataset", UNSET)

        image_create_config = cls(
            method=method,
            force=force,
            tag=tag,
            url=url,
            zfs_dataset=zfs_dataset,
        )

        image_create_config.additional_properties = d
        return image_create_config

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
