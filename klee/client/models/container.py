from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.container_network_driver import ContainerNetworkDriver
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.public_port import PublicPort


T = TypeVar("T", bound="Container")


@_attrs_define
class Container:
    """Summary description of a container

    Attributes:
        cmd (Union[Unset, List[str]]): Command being used when starting the container
        created (Union[Unset, str]): When the container was created
        dataset (Union[Unset, str]): ZFS dataset of the container
        env (Union[Unset, List[str]]): List of environment variables used when the container is used. This list will be
            merged with environment variables defined by the image. The values in this list takes precedence if the variable
            is defined in both places. Example: ['DEBUG=0', 'LANG=da_DK.UTF-8'].
        id (Union[Unset, str]): The id of the container
        image_id (Union[Unset, str]): The id of the image that this container was created from
        jail_param (Union[Unset, List[str]]): List of jail parameters (see jail(8) for details) Example:
            ['allow.raw_sockets=true', 'osrelease=kleenejail'].
        name (Union[Unset, str]): Name of the container.
        network_driver (Union[Unset, ContainerNetworkDriver]): What kind of network driver is the container using.
            Possible values are `ipnet`, `host`, `vnet`, `disabled`.
             Example: ipnet.
        public_ports (Union[Unset, List['PublicPort']]): FIXME
        running (Union[Unset, bool]): whether or not the container is running
        user (Union[Unset, str]): The default user used when creating execution instances in the container.
    """

    cmd: Union[Unset, List[str]] = UNSET
    created: Union[Unset, str] = UNSET
    dataset: Union[Unset, str] = UNSET
    env: Union[Unset, List[str]] = UNSET
    id: Union[Unset, str] = UNSET
    image_id: Union[Unset, str] = UNSET
    jail_param: Union[Unset, List[str]] = UNSET
    name: Union[Unset, str] = UNSET
    network_driver: Union[Unset, ContainerNetworkDriver] = UNSET
    public_ports: Union[Unset, List["PublicPort"]] = UNSET
    running: Union[Unset, bool] = UNSET
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
        image_id = self.image_id
        jail_param: Union[Unset, List[str]] = UNSET
        if not isinstance(self.jail_param, Unset):
            jail_param = self.jail_param

        name = self.name
        network_driver: Union[Unset, str] = UNSET
        if not isinstance(self.network_driver, Unset):
            network_driver = self.network_driver.value

        public_ports: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.public_ports, Unset):
            public_ports = []
            for public_ports_item_data in self.public_ports:
                public_ports_item = public_ports_item_data.to_dict()

                public_ports.append(public_ports_item)

        running = self.running
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
        if image_id is not UNSET:
            field_dict["image_id"] = image_id
        if jail_param is not UNSET:
            field_dict["jail_param"] = jail_param
        if name is not UNSET:
            field_dict["name"] = name
        if network_driver is not UNSET:
            field_dict["network_driver"] = network_driver
        if public_ports is not UNSET:
            field_dict["public_ports"] = public_ports
        if running is not UNSET:
            field_dict["running"] = running
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.public_port import PublicPort

        d = src_dict.copy()
        cmd = cast(List[str], d.pop("cmd", UNSET))

        created = d.pop("created", UNSET)

        dataset = d.pop("dataset", UNSET)

        env = cast(List[str], d.pop("env", UNSET))

        id = d.pop("id", UNSET)

        image_id = d.pop("image_id", UNSET)

        jail_param = cast(List[str], d.pop("jail_param", UNSET))

        name = d.pop("name", UNSET)

        _network_driver = d.pop("network_driver", UNSET)
        network_driver: Union[Unset, ContainerNetworkDriver]
        if isinstance(_network_driver, Unset):
            network_driver = UNSET
        else:
            network_driver = ContainerNetworkDriver(_network_driver)

        public_ports = []
        _public_ports = d.pop("public_ports", UNSET)
        for public_ports_item_data in _public_ports or []:
            public_ports_item = PublicPort.from_dict(public_ports_item_data)

            public_ports.append(public_ports_item)

        running = d.pop("running", UNSET)

        user = d.pop("user", UNSET)

        container = cls(
            cmd=cmd,
            created=created,
            dataset=dataset,
            env=env,
            id=id,
            image_id=image_id,
            jail_param=jail_param,
            name=name,
            network_driver=network_driver,
            public_ports=public_ports,
            running=running,
            user=user,
        )

        container.additional_properties = d
        return container

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
