from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.container_config_network_driver import ContainerConfigNetworkDriver
from ..models.container_config_restart_policy import ContainerConfigRestartPolicy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mount_point_config import MountPointConfig
    from ..models.published_port_config import PublishedPortConfig


T = TypeVar("T", bound="ContainerConfig")


@_attrs_define
class ContainerConfig:
    """
    Attributes:
        cmd (Union[Unset, None, List[str]]): Command to execute when the container is started. If `[]` is specified the
            command from the image is used. Example: ['/bin/sh', '-c', 'ls /'].
        env (Union[Unset, None, List[str]]): List of environment variables when using the container. This list will be
            merged with environment variables defined by the image. The values in this list takes precedence if the variable
            is defined in both. Example: ['DEBUG=0', 'LANG=da_DK.UTF-8'].
        image (Union[Unset, None, str]): The name or id and possibly a snapshot of the image used for creating the
            container.
            The parameter uses the followinge format:

            - `<image_id>[@<snapshot_id>]` or
            - `<name>[:<tag>][@<snapshot_id>]`.

            If `<tag>` is omitted, `latest` is assumed.
             Example: ['FreeBSD:13.2-STABLE', 'FreeBSD:13.2-STABLE@6b3c821605d4', '48fa55889b0f',
            '48fa55889b0f@2028818d6f06'].
        jail_param (Union[Unset, None, List[str]]): List of jail parameters to use for the container.
            See the [jails manual page](https://man.freebsd.org/cgi/man.cgi?query=jail) for an explanation of what jail
            parameters is,
            and the [Kleene documentation](/run/jail-parameters/) for an explanation of how they are used by Kleene.
             Example: ['allow.raw_sockets=true', 'osrelease=kleenejail'].
        mounts (Union[Unset, None, List['MountPointConfig']]): List of files/directories/volumes on the host filesystem
            that should be mounted into the container. Example: [{'destination': '/mnt/db', 'source': 'database', 'type':
            'volume'}, {'destination': '/webapp', 'source': '/home/me/develop/webapp', 'type': 'nullfs'}].
        name (Union[Unset, None, str]): Name of the container. Must match `/?[a-zA-Z0-9][a-zA-Z0-9_.-]+`.
        network_driver (Union[Unset, ContainerConfigNetworkDriver]): What kind of network driver should the container
            use.
            Possible values are `ipnet`, `host`, `vnet`, `disabled`.
             Default: ContainerConfigNetworkDriver.IPNET. Example: host.
        persist (Union[Unset, None, bool]): Whether or not this container will be removed by pruning. Example: True.
        public_ports (Union[Unset, None, List['PublishedPortConfig']]): Listening ports on network interfaces that
            redirect incoming traffic to the container. Example: [{'container_port': '8000', 'host_port': '8080',
            'interfaces': ['em0'], 'properties': 'tcp'}].
        restart_policy (Union[Unset, None, ContainerConfigRestartPolicy]): Restarting policy of the container:

            - `"no"`: There is no automatic restart of the container
            - `"on-startup"`: The container is started each time Kleened is.
             Default: ContainerConfigRestartPolicy.NO. Example: on-startup.
        user (Union[Unset, None, str]): User that executes the command (cmd).
            If user is set to `""`, the user from the image will be used, which in turn is 'root' if no user is specified
            there.

            This parameter will be overwritten by the jail parameter `exec.jail_user` if it is set.
             Default: ''.
    """

    cmd: Union[Unset, None, List[str]] = UNSET
    env: Union[Unset, None, List[str]] = UNSET
    image: Union[Unset, None, str] = UNSET
    jail_param: Union[Unset, None, List[str]] = UNSET
    mounts: Union[Unset, None, List["MountPointConfig"]] = UNSET
    name: Union[Unset, None, str] = UNSET
    network_driver: Union[Unset, ContainerConfigNetworkDriver] = (
        ContainerConfigNetworkDriver.IPNET
    )
    persist: Union[Unset, None, bool] = False
    public_ports: Union[Unset, None, List["PublishedPortConfig"]] = UNSET
    restart_policy: Union[Unset, None, ContainerConfigRestartPolicy] = (
        ContainerConfigRestartPolicy.NO
    )
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

        persist = self.persist
        public_ports: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.public_ports, Unset):
            if self.public_ports is None:
                public_ports = None
            else:
                public_ports = []
                for public_ports_item_data in self.public_ports:
                    public_ports_item = public_ports_item_data.to_dict()

                    public_ports.append(public_ports_item)

        restart_policy: Union[Unset, None, str] = UNSET
        if not isinstance(self.restart_policy, Unset):
            restart_policy = self.restart_policy.value if self.restart_policy else None

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
        if persist is not UNSET:
            field_dict["persist"] = persist
        if public_ports is not UNSET:
            field_dict["public_ports"] = public_ports
        if restart_policy is not UNSET:
            field_dict["restart_policy"] = restart_policy
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.mount_point_config import MountPointConfig
        from ..models.published_port_config import PublishedPortConfig

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

        persist = d.pop("persist", UNSET)

        public_ports = []
        _public_ports = d.pop("public_ports", UNSET)
        for public_ports_item_data in _public_ports or []:
            public_ports_item = PublishedPortConfig.from_dict(public_ports_item_data)

            public_ports.append(public_ports_item)

        _restart_policy = d.pop("restart_policy", UNSET)
        restart_policy: Union[Unset, None, ContainerConfigRestartPolicy]
        if _restart_policy is None:
            restart_policy = None
        elif isinstance(_restart_policy, Unset):
            restart_policy = UNSET
        else:
            restart_policy = ContainerConfigRestartPolicy(_restart_policy)

        user = d.pop("user", UNSET)

        container_config = cls(
            cmd=cmd,
            env=env,
            image=image,
            jail_param=jail_param,
            mounts=mounts,
            name=name,
            network_driver=network_driver,
            persist=persist,
            public_ports=public_ports,
            restart_policy=restart_policy,
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
