from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deployment_config_containers_item import (
        DeploymentConfigContainersItem,
    )
    from ..models.image_build_config import ImageBuildConfig
    from ..models.image_create_config import ImageCreateConfig
    from ..models.network_config import NetworkConfig
    from ..models.volume_config import VolumeConfig


T = TypeVar("T", bound="DeploymentConfig")


@_attrs_define
class DeploymentConfig:
    """
    Attributes:
        containers (Union[Unset, List['DeploymentConfigContainersItem']]): Deployment containers
        images (Union[Unset, List[Union['ImageBuildConfig', 'ImageCreateConfig']]]): Deployment images.
        networks (Union[Unset, List['NetworkConfig']]): Deployment networks
        volumes (Union[Unset, List['VolumeConfig']]): Deployment volumes
    """

    containers: Union[Unset, List["DeploymentConfigContainersItem"]] = UNSET
    images: Union[Unset, List[Union["ImageBuildConfig", "ImageCreateConfig"]]] = UNSET
    networks: Union[Unset, List["NetworkConfig"]] = UNSET
    volumes: Union[Unset, List["VolumeConfig"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.image_build_config import ImageBuildConfig

        containers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.containers, Unset):
            containers = []
            for containers_item_data in self.containers:
                containers_item = containers_item_data.to_dict()

                containers.append(containers_item)

        images: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.images, Unset):
            images = []
            for images_item_data in self.images:
                images_item: Dict[str, Any]

                if isinstance(images_item_data, ImageBuildConfig):
                    images_item = images_item_data.to_dict()

                else:
                    images_item = images_item_data.to_dict()

                images.append(images_item)

        networks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.networks, Unset):
            networks = []
            for networks_item_data in self.networks:
                networks_item = networks_item_data.to_dict()

                networks.append(networks_item)

        volumes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.volumes, Unset):
            volumes = []
            for volumes_item_data in self.volumes:
                volumes_item = volumes_item_data.to_dict()

                volumes.append(volumes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if containers is not UNSET:
            field_dict["containers"] = containers
        if images is not UNSET:
            field_dict["images"] = images
        if networks is not UNSET:
            field_dict["networks"] = networks
        if volumes is not UNSET:
            field_dict["volumes"] = volumes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.deployment_config_containers_item import (
            DeploymentConfigContainersItem,
        )
        from ..models.image_build_config import ImageBuildConfig
        from ..models.image_create_config import ImageCreateConfig
        from ..models.network_config import NetworkConfig
        from ..models.volume_config import VolumeConfig

        d = src_dict.copy()
        containers = []
        _containers = d.pop("containers", UNSET)
        for containers_item_data in _containers or []:
            containers_item = DeploymentConfigContainersItem.from_dict(
                containers_item_data
            )

            containers.append(containers_item)

        images = []
        _images = d.pop("images", UNSET)
        for images_item_data in _images or []:

            def _parse_images_item(
                data: object,
            ) -> Union["ImageBuildConfig", "ImageCreateConfig"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    images_item_type_0 = ImageBuildConfig.from_dict(data)

                    return images_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                images_item_type_1 = ImageCreateConfig.from_dict(data)

                return images_item_type_1

            images_item = _parse_images_item(images_item_data)

            images.append(images_item)

        networks = []
        _networks = d.pop("networks", UNSET)
        for networks_item_data in _networks or []:
            networks_item = NetworkConfig.from_dict(networks_item_data)

            networks.append(networks_item)

        volumes = []
        _volumes = d.pop("volumes", UNSET)
        for volumes_item_data in _volumes or []:
            volumes_item = VolumeConfig.from_dict(volumes_item_data)

            volumes.append(volumes_item)

        deployment_config = cls(
            containers=containers,
            images=images,
            networks=networks,
            volumes=volumes,
        )

        deployment_config.additional_properties = d
        return deployment_config

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
