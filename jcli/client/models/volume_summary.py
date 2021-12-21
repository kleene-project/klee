from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="VolumeSummary")


@attr.s(auto_attribs=True)
class VolumeSummary:
    """summary description of a volume

    Attributes:
        created (Union[Unset, str]): when the volume was created
        dataset (Union[Unset, str]): underlying zfs dataset of the volume
        mountpoint (Union[Unset, str]): main mountpoint of the volume (the mountpoint shown with 'zfs list')
        name (Union[Unset, str]): Name of the volume
    """

    created: Union[Unset, str] = UNSET
    dataset: Union[Unset, str] = UNSET
    mountpoint: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created = self.created
        dataset = self.dataset
        mountpoint = self.mountpoint
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created is not UNSET:
            field_dict["created"] = created
        if dataset is not UNSET:
            field_dict["dataset"] = dataset
        if mountpoint is not UNSET:
            field_dict["mountpoint"] = mountpoint
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created = d.pop("created", UNSET)

        dataset = d.pop("dataset", UNSET)

        mountpoint = d.pop("mountpoint", UNSET)

        name = d.pop("name", UNSET)

        volume_summary = cls(
            created=created,
            dataset=dataset,
            mountpoint=mountpoint,
            name=name,
        )

        volume_summary.additional_properties = d
        return volume_summary

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
