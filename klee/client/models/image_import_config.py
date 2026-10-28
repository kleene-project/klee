from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImageImportConfig")


@_attrs_define
class ImageImportConfig:
    """Configuration for importing an OCI image layout archive.

    Attributes:
        url (str): URL or local path to an OCI image layout archive (a `.txz`/`.tar` file
            containing `oci-layout`, `index.json` and `blobs/`, like the container
            images published on download.freebsd.org).
        platform (Union[Unset, None, str]): `os/architecture` selector when the archive is a multi-platform index
            (e.g. `freebsd/amd64`). Defaults to the host's own os/architecture
            (from `uname(1)`) when the index carries platform information, and to
            the first manifest otherwise.
        tag (Union[Unset, str]): Name and optionally a tag in the `name:tag` format for the imported image.
            If `tag` is omitted, the default value `latest` is used.
             Default: ''.
    """

    url: str
    platform: Union[Unset, None, str] = UNSET
    tag: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        url = self.url
        platform = self.platform
        tag = self.tag

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
            }
        )
        if platform is not UNSET:
            field_dict["platform"] = platform
        if tag is not UNSET:
            field_dict["tag"] = tag

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        url = d.pop("url")

        platform = d.pop("platform", UNSET)

        tag = d.pop("tag", UNSET)

        image_import_config = cls(
            url=url,
            platform=platform,
            tag=tag,
        )

        image_import_config.additional_properties = d
        return image_import_config

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
