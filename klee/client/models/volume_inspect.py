from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mount_point import MountPoint
    from ..models.volume import Volume


T = TypeVar("T", bound="VolumeInspect")


@_attrs_define
class VolumeInspect:
    """Detailed information on a volume.

    Attributes:
        mountpoints (Union[Unset, List['MountPoint']]): Mountpoints of the volume.
        volume (Union[Unset, Volume]): Volume object used for persistent storage in containers.
    """

    mountpoints: Union[Unset, List["MountPoint"]] = UNSET
    volume: Union[Unset, "Volume"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        mountpoints: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.mountpoints, Unset):
            mountpoints = []
            for mountpoints_item_data in self.mountpoints:
                mountpoints_item = mountpoints_item_data.to_dict()

                mountpoints.append(mountpoints_item)

        volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.volume, Unset):
            volume = self.volume.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mountpoints is not UNSET:
            field_dict["mountpoints"] = mountpoints
        if volume is not UNSET:
            field_dict["volume"] = volume

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.mount_point import MountPoint
        from ..models.volume import Volume

        d = src_dict.copy()
        mountpoints = []
        _mountpoints = d.pop("mountpoints", UNSET)
        for mountpoints_item_data in _mountpoints or []:
            mountpoints_item = MountPoint.from_dict(mountpoints_item_data)

            mountpoints.append(mountpoints_item)

        _volume = d.pop("volume", UNSET)
        volume: Union[Unset, Volume]
        if isinstance(_volume, Unset):
            volume = UNSET
        else:
            volume = Volume.from_dict(_volume)

        volume_inspect = cls(
            mountpoints=mountpoints,
            volume=volume,
        )

        volume_inspect.additional_properties = d
        return volume_inspect

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
