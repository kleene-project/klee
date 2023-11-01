from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MountPoint")


@_attrs_define
class MountPoint:
    """Detailed information on a volume.

    Attributes:
        container_id (Union[Unset, str]): ID of the container where the volume is mounted.
        location (Union[Unset, str]): Location of the mount within the container.
        read_only (Union[Unset, bool]): Whether this mountpoint is read-only.
        volume_name (Union[Unset, str]): Name of the volume
    """

    container_id: Union[Unset, str] = UNSET
    location: Union[Unset, str] = UNSET
    read_only: Union[Unset, bool] = UNSET
    volume_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container_id = self.container_id
        location = self.location
        read_only = self.read_only
        volume_name = self.volume_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container_id is not UNSET:
            field_dict["container_id"] = container_id
        if location is not UNSET:
            field_dict["location"] = location
        if read_only is not UNSET:
            field_dict["read_only"] = read_only
        if volume_name is not UNSET:
            field_dict["volume_name"] = volume_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_id = d.pop("container_id", UNSET)

        location = d.pop("location", UNSET)

        read_only = d.pop("read_only", UNSET)

        volume_name = d.pop("volume_name", UNSET)

        mount_point = cls(
            container_id=container_id,
            location=location,
            read_only=read_only,
            volume_name=volume_name,
        )

        mount_point.additional_properties = d
        return mount_point

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
