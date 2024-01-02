from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.container_config_network_driver import ContainerConfigNetworkDriver
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mount_point_config import MountPointConfig


T = TypeVar("T", bound="ContainerConfig")


@_attrs_define
class ContainerConfig:
    """
    Attributes:
        cmd (Union[Unset, None, List[str]]): Command to execute when the container is started. If no command is
            specified the command from the image is used. Example: ['/bin/sh', '-c', 'ls /'].
        env (Union[Unset, None, List[str]]): List of environment variables when using the container. This list will be
            merged with environment variables defined by the image. The values in this list takes precedence if the variable
            is defined in both. Example: ['DEBUG=0', 'LANG=da_DK.UTF-8'].
        image (Union[Unset, str]): The name or id and possibly a snapshot of the image used for creating the container.
            The parameter uses the followinge format:

            - `<image_id>[@<snapshot_id>]` or
            - `<name>[:<tag>][@<snapshot_id>]`.

            If `<tag>` is omitted, `latest` is assumed.
             Example: ['FreeBSD:13.2-STABLE', 'FreeBSD:13.2-STABLE@6b3c821605d4', '48fa55889b0f',
            '48fa55889b0f@2028818d6f06'].
        jail_param (Union[Unset, None, List[str]]): List of jail parameters to use for the container.
            See the [`jails manual page`](https://man.freebsd.org/cgi/man.cgi?query=jail) for details.

            A few parameters have some special behavior in Kleene:

            - `exec.jail_user`: If not explicitly set, the value of the `user` parameter will be used.
            - `mount.devfs`/`exec.clean`: If not explicitly set, `mount.devfs=true`/`exec.clean=true` will be used.

            So, if you do not want `exec.clean` and `mount.devfs` enabled, you must actively disable them.
             Example: ['allow.raw_sockets=true', 'osrelease=kleenejail'].
        mounts (Union[Unset, None, List['MountPointConfig']]): List of files/directories/volumes on the host filesystem
            that should be mounted into the container.
        name (Union[Unset, None, str]): Name of the container. Must match `/?[a-zA-Z0-9][a-zA-Z0-9_.-]+`.
        network_driver (Union[Unset, ContainerConfigNetworkDriver]): What kind of network driver should the container
            use.
            Possible values are `ipnet`, `host`, `vnet`, `disabled`.
             Default: ContainerConfigNetworkDriver.IPNET. Example: host.
        user (Union[Unset, None, str]): User that executes the command (cmd).
            If no user is set, the user from the image will be used, which in turn is 'root' if no user is specified there.

            This parameter will be overwritten by the jail parameter `exec.jail_user` if it is set.
             Default: ''.
    """

    cmd: Union[Unset, None, List[str]] = UNSET
    env: Union[Unset, None, List[str]] = UNSET
    image: Union[Unset, str] = UNSET
    jail_param: Union[Unset, None, List[str]] = UNSET
    mounts: Union[Unset, None, List["MountPointConfig"]] = UNSET
    name: Union[Unset, None, str] = UNSET
    network_driver: Union[
        Unset, ContainerConfigNetworkDriver
    ] = ContainerConfigNetworkDriver.IPNET
    user: Union[Unset, None, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cmd: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.cmd, Unset):
            if self.cmd is None:
                cmd = None
            else:
                cmd = self.cmd

        env: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.env, Unset):
            if self.env is None:
                env = None
            else:
                env = self.env

        image = self.image
        jail_param: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.jail_param, Unset):
            if self.jail_param is None:
                jail_param = None
            else:
                jail_param = self.jail_param

        mounts: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.mounts, Unset):
            if self.mounts is None:
                mounts = None
            else:
                mounts = []
                for mounts_item_data in self.mounts:
                    mounts_item = mounts_item_data.to_dict()

                    mounts.append(mounts_item)

        name = self.name
        network_driver: Union[Unset, str] = UNSET
        if not isinstance(self.network_driver, Unset):
            network_driver = self.network_driver.value

        user = self.user

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
        if mounts is not UNSET:
            field_dict["mounts"] = mounts
        if name is not UNSET:
            field_dict["name"] = name
        if network_driver is not UNSET:
            field_dict["network_driver"] = network_driver
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.mount_point_config import MountPointConfig

        d = src_dict.copy()
        cmd = cast(List[str], d.pop("cmd", UNSET))

        env = cast(List[str], d.pop("env", UNSET))

        image = d.pop("image", UNSET)

        jail_param = cast(List[str], d.pop("jail_param", UNSET))

        mounts = []
        _mounts = d.pop("mounts", UNSET)
        for mounts_item_data in _mounts or []:
            mounts_item = MountPointConfig.from_dict(mounts_item_data)

            mounts.append(mounts_item)

        name = d.pop("name", UNSET)

        _network_driver = d.pop("network_driver", UNSET)
        network_driver: Union[Unset, ContainerConfigNetworkDriver]
        if isinstance(_network_driver, Unset):
            network_driver = UNSET
        else:
            network_driver = ContainerConfigNetworkDriver(_network_driver)

        user = d.pop("user", UNSET)

        container_config = cls(
            cmd=cmd,
            env=env,
            image=image,
            jail_param=jail_param,
            mounts=mounts,
            name=name,
            network_driver=network_driver,
            user=user,
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
