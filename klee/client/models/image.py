from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Image")


@_attrs_define
class Image:
    """the image metadata

    Attributes:
        cmd (Union[Unset, List[str]]): Default command used when creating a container from this image Example:
            ['/bin/sh', '-c', '/bin/ls'].
        created (Union[Unset, str]): When the image was created
        dataset (Union[Unset, str]): ZFS dataset of the image
        env (Union[Unset, List[str]]): Environment variables and their values to set before running command. Example:
            ['PWD=/roo/', 'JAIL_MGMT_ENGINE=kleene'].
        id (Union[Unset, str]): The id of the image
        instructions (Union[Unset, List[List[str]]]): Instructions and their corresponding snapshots (if they exist)
            that were used to build the image.
            Each item in the array consists of a 2-element array `["<instruction>","<snapshot>"]`
            containing one instruction and possibly its snapshot.
            The latter is only be present with `RUN` or `COPY` instructions that ran succesfully.
            Otherwise `<snapshot>` is empty.
        name (Union[Unset, str]): Name of the image
        tag (Union[Unset, str]): Tag of the image
        user (Union[Unset, str]): User used for running `cmd`
    """

    cmd: Union[Unset, List[str]] = UNSET
    created: Union[Unset, str] = UNSET
    dataset: Union[Unset, str] = UNSET
    env: Union[Unset, List[str]] = UNSET
    id: Union[Unset, str] = UNSET
    instructions: Union[Unset, List[List[str]]] = UNSET
    name: Union[Unset, str] = UNSET
    tag: Union[Unset, str] = UNSET
    user: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cmd: Union[Unset, List[str]] = UNSET
        if not isinstance(self.cmd, Unset):
            cmd = self.cmd

        created = self.created
        dataset = self.dataset
        env: Union[Unset, List[str]] = UNSET
        if not isinstance(self.env, Unset):
            env = self.env

        id = self.id
        instructions: Union[Unset, List[List[str]]] = UNSET
        if not isinstance(self.instructions, Unset):
            instructions = []
            for instructions_item_data in self.instructions:
                instructions_item = instructions_item_data

                instructions.append(instructions_item)

        name = self.name
        tag = self.tag
        user = self.user

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cmd is not UNSET:
            field_dict["cmd"] = cmd
        if created is not UNSET:
            field_dict["created"] = created
        if dataset is not UNSET:
            field_dict["dataset"] = dataset
        if env is not UNSET:
            field_dict["env"] = env
        if id is not UNSET:
            field_dict["id"] = id
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if name is not UNSET:
            field_dict["name"] = name
        if tag is not UNSET:
            field_dict["tag"] = tag
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cmd = cast(List[str], d.pop("cmd", UNSET))

        created = d.pop("created", UNSET)

        dataset = d.pop("dataset", UNSET)

        env = cast(List[str], d.pop("env", UNSET))

        id = d.pop("id", UNSET)

        instructions = []
        _instructions = d.pop("instructions", UNSET)
        for instructions_item_data in _instructions or []:
            instructions_item = cast(List[str], instructions_item_data)

            instructions.append(instructions_item)

        name = d.pop("name", UNSET)

        tag = d.pop("tag", UNSET)

        user = d.pop("user", UNSET)

        image = cls(
            cmd=cmd,
            created=created,
            dataset=dataset,
            env=env,
            id=id,
            instructions=instructions,
            name=name,
            tag=tag,
            user=user,
        )

        image.additional_properties = d
        return image

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
