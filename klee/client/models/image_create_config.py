from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.image_create_config_method import ImageCreateConfigMethod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageCreateConfig")


@_attrs_define
class ImageCreateConfig:
    """Configuration for the creation of base images.

    Attributes:
        method (ImageCreateConfigMethod): There are four methods for creating a new base image:

            - `fetch`: Fetch a release/snapshot of the base system from `url` and use it for image creation.
            - `fetch-auto`: Automatically fetch a release/snapshot from the offical FreeBSD mirrors, based on information
            from `uname(1)`.
            - `zfs-copy`: Create the base image based on a copy of `zfs_dataset`.
            - `zfs-clone`: Create the base image based on a clone of `zfs_dataset`.
        autotag (Union[Unset, bool]): **`fetch-auto` method only**

            Whether or not to auto-genereate a nametag `FreeBSD-<version>:latest` based on `uname(1)`.
            Overrides `tag` if set to `true`.
        dns (Union[Unset, bool]): Whether or not to copy `/etc/resolv.conf` from the host to the new image. Default:
            True.
        force (Union[Unset, bool]): **`fetch-auto` method only**

            Ignore any discrepancies in the output of `uname(1)` when determining the FreeBSD version.
        tag (Union[Unset, str]): Name and optionally a tag in the `name:tag` format. If `tag` is omitted, the default
            value `latest` is used.
             Default: ''.
        url (Union[Unset, str]): **`fetch` method only**

            URL to the base system (a `base.txz` file) that Kleened should use to create the base image.
             Default: ''.
        zfs_dataset (Union[Unset, str]): **`zfs-*` methods only**

            ZFS dataset that the image should be based on.
             Default: ''.
    """

    method: ImageCreateConfigMethod
    autotag: Union[Unset, bool] = False
    dns: Union[Unset, bool] = True
    force: Union[Unset, bool] = False
    tag: Union[Unset, str] = ""
    url: Union[Unset, str] = ""
    zfs_dataset: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        method = self.method.value

        autotag = self.autotag
        dns = self.dns
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
        if autotag is not UNSET:
            field_dict["autotag"] = autotag
        if dns is not UNSET:
            field_dict["dns"] = dns
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

        autotag = d.pop("autotag", UNSET)

        dns = d.pop("dns", UNSET)

        force = d.pop("force", UNSET)

        tag = d.pop("tag", UNSET)

        url = d.pop("url", UNSET)

        zfs_dataset = d.pop("zfs_dataset", UNSET)

        image_create_config = cls(
            method=method,
            autotag=autotag,
            dns=dns,
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
