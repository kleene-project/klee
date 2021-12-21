from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Image")


@attr.s(auto_attribs=True)
class Image:
    """the image metadata

    Attributes:
        command (Union[Unset, List[str]]): Default command used when creating a container from this image Example:
            ['/bin/sh', '-c', '/bin/ls'].
        created (Union[Unset, str]): When the image was created
        env_vars (Union[Unset, List[str]]): List of environment variables and their values to set before running
            command. Example: ['PWD=/roo/', 'JAIL_MGMT_ENGINE=jocker'].
        id (Union[Unset, str]): The id of the image
        layer_id (Union[Unset, str]): Id of the layer containing the image
        name (Union[Unset, str]): Name of the image
        tag (Union[Unset, str]): Tag of the image
        user (Union[Unset, str]): user used when executing the command
    """

    command: Union[Unset, List[str]] = UNSET
    created: Union[Unset, str] = UNSET
    env_vars: Union[Unset, List[str]] = UNSET
    id: Union[Unset, str] = UNSET
    layer_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    tag: Union[Unset, str] = UNSET
    user: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        command: Union[Unset, List[str]] = UNSET
        if not isinstance(self.command, Unset):
            command = self.command

        created = self.created
        env_vars: Union[Unset, List[str]] = UNSET
        if not isinstance(self.env_vars, Unset):
            env_vars = self.env_vars

        id = self.id
        layer_id = self.layer_id
        name = self.name
        tag = self.tag
        user = self.user

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if command is not UNSET:
            field_dict["command"] = command
        if created is not UNSET:
            field_dict["created"] = created
        if env_vars is not UNSET:
            field_dict["env_vars"] = env_vars
        if id is not UNSET:
            field_dict["id"] = id
        if layer_id is not UNSET:
            field_dict["layer_id"] = layer_id
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
        command = cast(List[str], d.pop("command", UNSET))

        created = d.pop("created", UNSET)

        env_vars = cast(List[str], d.pop("env_vars", UNSET))

        id = d.pop("id", UNSET)

        layer_id = d.pop("layer_id", UNSET)

        name = d.pop("name", UNSET)

        tag = d.pop("tag", UNSET)

        user = d.pop("user", UNSET)

        image = cls(
            command=command,
            created=created,
            env_vars=env_vars,
            id=id,
            layer_id=layer_id,
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
