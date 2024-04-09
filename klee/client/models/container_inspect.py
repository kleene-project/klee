from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.container import Container
    from ..models.end_point import EndPoint
    from ..models.mount_point import MountPoint


T = TypeVar("T", bound="ContainerInspect")


@_attrs_define
class ContainerInspect:
    """Detailed information on a container.

    Attributes:
        container (Union[Unset, Container]): Kleene container
        container_endpoints (Union[Unset, List['EndPoint']]): Endpoints of the container.
        container_mountpoints (Union[Unset, List['MountPoint']]): Mountpoints of the container.
    """

    container: Union[Unset, "Container"] = UNSET
    container_endpoints: Union[Unset, List["EndPoint"]] = UNSET
    container_mountpoints: Union[Unset, List["MountPoint"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.container, Unset):
            container = self.container.to_dict()

        container_endpoints: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.container_endpoints, Unset):
            container_endpoints = []
            for container_endpoints_item_data in self.container_endpoints:
                container_endpoints_item = container_endpoints_item_data.to_dict()

                container_endpoints.append(container_endpoints_item)

        container_mountpoints: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.container_mountpoints, Unset):
            container_mountpoints = []
            for container_mountpoints_item_data in self.container_mountpoints:
                container_mountpoints_item = container_mountpoints_item_data.to_dict()

                container_mountpoints.append(container_mountpoints_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container is not UNSET:
            field_dict["container"] = container
        if container_endpoints is not UNSET:
            field_dict["container_endpoints"] = container_endpoints
        if container_mountpoints is not UNSET:
            field_dict["container_mountpoints"] = container_mountpoints

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.container import Container
        from ..models.end_point import EndPoint
        from ..models.mount_point import MountPoint

        d = src_dict.copy()
        _container = d.pop("container", UNSET)
        container: Union[Unset, Container]
        if isinstance(_container, Unset):
            container = UNSET
        else:
            container = Container.from_dict(_container)

        container_endpoints = []
        _container_endpoints = d.pop("container_endpoints", UNSET)
        for container_endpoints_item_data in _container_endpoints or []:
            container_endpoints_item = EndPoint.from_dict(container_endpoints_item_data)

            container_endpoints.append(container_endpoints_item)

        container_mountpoints = []
        _container_mountpoints = d.pop("container_mountpoints", UNSET)
        for container_mountpoints_item_data in _container_mountpoints or []:
            container_mountpoints_item = MountPoint.from_dict(
                container_mountpoints_item_data
            )

            container_mountpoints.append(container_mountpoints_item)

        container_inspect = cls(
            container=container,
            container_endpoints=container_endpoints,
            container_mountpoints=container_mountpoints,
        )

        container_inspect.additional_properties = d
        return container_inspect

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
