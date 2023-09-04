from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerConfig")


@attr.s(auto_attribs=True)
class ContainerConfig:
    """
    Attributes:
        cmd (Union[Unset, List[str]]): Command to execute when the container is started. If no command is specified the
            command from the image is used. Example: ['/bin/sh', '-c', 'ls /'].
        env (Union[Unset, List[str]]): List of environment variables when using the container. This list will be merged
            with environment variables defined by the image. The values in this list takes precedence if the variable is
            defined in both. Example: ['DEBUG=0', 'LANG=da_DK.UTF-8'].
        image (Union[Unset, str]): The name or id of the image used for creating the container Example: FreeBSD-13.0.
        jail_param (Union[Unset, List[str]]): List of `jail(8)` parameters to use for the container. Example:
            ['allow.raw_sockets=true', 'osrelease=kleenejail'].
        user (Union[Unset, str]): User that executes the command (cmd). If no user is set the user from the image will
            be used (which in turn is 'root' if no user is specified there). Default: ''.
        volumes (Union[Unset, List[str]]): List of volumes that should be mounted into the container
    """

    cmd: Union[Unset, List[str]] = UNSET
    env: Union[Unset, List[str]] = UNSET
    image: Union[Unset, str] = UNSET
    jail_param: Union[Unset, List[str]] = UNSET
    user: Union[Unset, str] = ""
    volumes: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cmd: Union[Unset, List[str]] = UNSET
        if not isinstance(self.cmd, Unset):
            cmd = self.cmd

        env: Union[Unset, List[str]] = UNSET
        if not isinstance(self.env, Unset):
            env = self.env

        image = self.image
        jail_param: Union[Unset, List[str]] = UNSET
        if not isinstance(self.jail_param, Unset):
            jail_param = self.jail_param

        user = self.user
        volumes: Union[Unset, List[str]] = UNSET
        if not isinstance(self.volumes, Unset):
            volumes = self.volumes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cmd is not UNSET:
            field_dict["cmd"] = cmd
        if env is not UNSET:
            field_dict["env"] = env
        if image is not UNSET:
            field_dict["image"] = image
        if jail_param is not UNSET:
            field_dict["jail_param"] = jail_param
        if user is not UNSET:
            field_dict["user"] = user
        if volumes is not UNSET:
            field_dict["volumes"] = volumes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cmd = cast(List[str], d.pop("cmd", UNSET))

        env = cast(List[str], d.pop("env", UNSET))

        image = d.pop("image", UNSET)

        jail_param = cast(List[str], d.pop("jail_param", UNSET))

        user = d.pop("user", UNSET)

        volumes = cast(List[str], d.pop("volumes", UNSET))

        container_config = cls(
            cmd=cmd,
            env=env,
            image=image,
            jail_param=jail_param,
            user=user,
            volumes=volumes,
        )

        container_config.additional_properties = d
        return container_config

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
