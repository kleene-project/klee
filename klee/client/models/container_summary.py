from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerSummary")


@_attrs_define
class ContainerSummary:
    """summary description of a container

    Attributes:
        cmd (Union[Unset, str]): Command being used when starting the container
        created (Union[Unset, str]): When the container was created
        id (Union[Unset, str]): The id of this container
        image_id (Union[Unset, str]): The id of the image that this container was created from
        image_name (Union[Unset, str]): Name of the image that this container was created from
        image_tag (Union[Unset, str]): Tag of the image that this container was created from
        jid (Union[Unset, None, int]): Jail ID if it is a running container
        name (Union[Unset, str]): Name of the container
        running (Union[Unset, bool]): whether or not the container is running
    """

    cmd: Union[Unset, str] = UNSET
    created: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    image_id: Union[Unset, str] = UNSET
    image_name: Union[Unset, str] = UNSET
    image_tag: Union[Unset, str] = UNSET
    jid: Union[Unset, None, int] = UNSET
    name: Union[Unset, str] = UNSET
    running: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cmd = self.cmd
        created = self.created
        id = self.id
        image_id = self.image_id
        image_name = self.image_name
        image_tag = self.image_tag
        jid = self.jid
        name = self.name
        running = self.running

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cmd is not UNSET:
            field_dict["cmd"] = cmd
        if created is not UNSET:
            field_dict["created"] = created
        if id is not UNSET:
            field_dict["id"] = id
        if image_id is not UNSET:
            field_dict["image_id"] = image_id
        if image_name is not UNSET:
            field_dict["image_name"] = image_name
        if image_tag is not UNSET:
            field_dict["image_tag"] = image_tag
        if jid is not UNSET:
            field_dict["jid"] = jid
        if name is not UNSET:
            field_dict["name"] = name
        if running is not UNSET:
            field_dict["running"] = running

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cmd = d.pop("cmd", UNSET)

        created = d.pop("created", UNSET)

        id = d.pop("id", UNSET)

        image_id = d.pop("image_id", UNSET)

        image_name = d.pop("image_name", UNSET)

        image_tag = d.pop("image_tag", UNSET)

        jid = d.pop("jid", UNSET)

        name = d.pop("name", UNSET)

        running = d.pop("running", UNSET)

        container_summary = cls(
            cmd=cmd,
            created=created,
            id=id,
            image_id=image_id,
            image_name=image_name,
            image_tag=image_tag,
            jid=jid,
            name=name,
            running=running,
        )

        container_summary.additional_properties = d
        return container_summary

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
