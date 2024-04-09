from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mount_point_config_type import MountPointConfigType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MountPointConfig")


@_attrs_define
class MountPointConfig:
    """Configuration for a mount point between the host file system and a container.

    There are two types of mount points:

    - `nullfs`: Mount a user-specified file or directory from the host machine into the container.
    - `volume`: Mount a Kleene volume into the container.

        Attributes:
            destination (Union[Unset, str]): Destination path of the mount within the container.
            read_only (Union[Unset, bool]): Whether the mountpoint should be read-only.
            source (Union[Unset, str]): Source used for the mount. Depends on `method`:

                - If `method` is `"volume"` then `source` should be a volume name
                - If `method`is `"nullfs"` then `source` should be an absolute path on the host
            type (Union[Unset, MountPointConfigType]): Type of mountpoint to create.
    """

    destination: Union[Unset, str] = UNSET
    read_only: Union[Unset, bool] = False
    source: Union[Unset, str] = UNSET
    type: Union[Unset, MountPointConfigType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        destination = self.destination
        read_only = self.read_only
        source = self.source
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        destination = d.pop("destination", UNSET)

        read_only = d.pop("read_only", UNSET)

        source = d.pop("source", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, MountPointConfigType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = MountPointConfigType(_type)

        mount_point_config = cls(
            destination=destination,
            read_only=read_only,
            source=source,
            type=type,
        )

        mount_point_config.additional_properties = d
        return mount_point_config

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
