from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExecConfig")


@_attrs_define
class ExecConfig:
    """Configuration of an executable to run within a container. Some of the configuration parameters will overwrite the
    corresponding parameters if they are defined in the container.

        Attributes:
            cmd (Union[Unset, List[str]]): Command to execute whithin the container. If `cmd` is set to `[]` the command
                will be inherited from the container. Example: ['/bin/sh', '-c', 'ls /'].
            container_id (Union[Unset, str]): Identifier of the container used as environemnt for the exec instance.
            env (Union[Unset, List[str]]): A list of environment variables in the form `["VAR=value", ...]` that is set when
                the command is executed.
                This list will be merged with environment variables defined in the container.
                The values in this list takes precedence if the variable is defined in both.
                 Example: ['DEBUG=0', 'LANG=da_DK.UTF-8'].
            tty (Union[Unset, bool]): Allocate a pseudo-TTY for the process.
            user (Union[Unset, str]): User that executes the command in the container. If the user is set to `""`, the user
                will be inherited from the container. Default: ''.
    """

    cmd: Union[Unset, List[str]] = UNSET
    container_id: Union[Unset, str] = UNSET
    env: Union[Unset, List[str]] = UNSET
    tty: Union[Unset, bool] = False
    user: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cmd: Union[Unset, List[str]] = UNSET
        if not isinstance(self.cmd, Unset):
            cmd = self.cmd

        container_id = self.container_id
        env: Union[Unset, List[str]] = UNSET
        if not isinstance(self.env, Unset):
            env = self.env

        tty = self.tty
        user = self.user

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cmd is not UNSET:
            field_dict["cmd"] = cmd
        if container_id is not UNSET:
            field_dict["container_id"] = container_id
        if env is not UNSET:
            field_dict["env"] = env
        if tty is not UNSET:
            field_dict["tty"] = tty
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cmd = cast(List[str], d.pop("cmd", UNSET))

        container_id = d.pop("container_id", UNSET)

        env = cast(List[str], d.pop("env", UNSET))

        tty = d.pop("tty", UNSET)

        user = d.pop("user", UNSET)

        exec_config = cls(
            cmd=cmd,
            container_id=container_id,
            env=env,
            tty=tty,
            user=user,
        )

        exec_config.additional_properties = d
        return exec_config

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
