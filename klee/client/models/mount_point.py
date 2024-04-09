from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mount_point_type import MountPointType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MountPoint")


@_attrs_define
class MountPoint:
    """Mount point between the host file system and a container.

    There are two types of mount points:

    - `nullfs`: Mount a user-specified file or directory from the host machine into the container.
    - `volume`: Mount a Kleene volume into the container.

        Attributes:
            container_id (Union[Unset, str]): ID of the container that the mountpoint belongs to.
            destination (Union[Unset, str]): Destination path of the mountpoint within the container.
            read_only (Union[Unset, bool]): Whether this mountpoint is read-only.
            source (Union[Unset, str]): Source used for the mount. Depends on `method`:

                - If `method` is `"volume"` then `source` should be a volume name
                - If `method`is `"nullfs"` then `source` should be an absolute path on the host
            type (Union[Unset, MountPointType]): Mounpoint type.
    """

    container_id: Union[Unset, str] = UNSET
    destination: Union[Unset, str] = UNSET
    read_only: Union[Unset, bool] = UNSET
    source: Union[Unset, str] = UNSET
    type: Union[Unset, MountPointType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container_id = self.container_id
        destination = self.destination
        read_only = self.read_only
        source = self.source
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container_id is not UNSET:
            field_dict["container_id"] = container_id
        if destination is not UNSET:
            field_dict["destination"] = destination
        if read_only is not UNSET:
            field_dict["read_only"] = read_only
        if source is not UNSET:
            field_dict["source"] = source
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_id = d.pop("container_id", UNSET)

        destination = d.pop("destination", UNSET)

        read_only = d.pop("read_only", UNSET)

        source = d.pop("source", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, MountPointType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = MountPointType(_type)

        mount_point = cls(
            container_id=container_id,
            destination=destination,
            read_only=read_only,
            source=source,
            type=type,
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
