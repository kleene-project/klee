from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.container_config import ContainerConfig
    from ..models.end_point_config import EndPointConfig
    from ..models.image_build_config_buildargs import ImageBuildConfigBuildargs


T = TypeVar("T", bound="ImageBuildConfig")


@_attrs_define
class ImageBuildConfig:
    """Configuration for an image build, including container configuration for the build container.

    Attributes:
        container_config (ContainerConfig):
        context (str): Location path on the Kleened host of the context used for the image build.
        buildargs (Union[Unset, ImageBuildConfigBuildargs]): Additional `ARG`-variables given as an object of string
            pairs.
            See the [`ARG` instruction documentation](/reference/dockerfile/#arg) for details.
             Example: {'JAIL_MGMT_ENGINE': 'kleene', 'USERNAME': 'Stephen'}.
        cleanup (Union[Unset, bool]): Whether or not to remove the image in case of a build failure. Default: True.
        dockerfile (Union[Unset, str]): Path of the Dockerfile used for the build. The path is relative to the context
            path. Default: 'Dockerfile'.
        networks (Union[Unset, List['EndPointConfig']]): List of endpoint-configs for the networks that the build
            container will be connected to.
        quiet (Union[Unset, bool]): Whether or not to send status messages of the build process to the client.
        tag (Union[Unset, str]): A name and optional tag to apply to the image in the `name:tag` format. If `tag` is
            omitted, the default value `latest` is used. Default: ''.
    """

    container_config: "ContainerConfig"
    context: str
    buildargs: Union[Unset, "ImageBuildConfigBuildargs"] = UNSET
    cleanup: Union[Unset, bool] = True
    dockerfile: Union[Unset, str] = "Dockerfile"
    networks: Union[Unset, List["EndPointConfig"]] = UNSET
    quiet: Union[Unset, bool] = False
    tag: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        container_config = self.container_config.to_dict()

        context = self.context
        buildargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.buildargs, Unset):
            buildargs = self.buildargs.to_dict()

        cleanup = self.cleanup
        dockerfile = self.dockerfile
        networks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.networks, Unset):
            networks = []
            for networks_item_data in self.networks:
                networks_item = networks_item_data.to_dict()

                networks.append(networks_item)

        quiet = self.quiet
        tag = self.tag

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "container_config": container_config,
                "context": context,
            }
        )
        if buildargs is not UNSET:
            field_dict["buildargs"] = buildargs
        if cleanup is not UNSET:
            field_dict["cleanup"] = cleanup
        if dockerfile is not UNSET:
            field_dict["dockerfile"] = dockerfile
        if networks is not UNSET:
            field_dict["networks"] = networks
        if quiet is not UNSET:
            field_dict["quiet"] = quiet
        if tag is not UNSET:
            field_dict["tag"] = tag

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.container_config import ContainerConfig
        from ..models.end_point_config import EndPointConfig
        from ..models.image_build_config_buildargs import ImageBuildConfigBuildargs

        d = src_dict.copy()
        container_config = ContainerConfig.from_dict(d.pop("container_config"))

        context = d.pop("context")

        _buildargs = d.pop("buildargs", UNSET)
        buildargs: Union[Unset, ImageBuildConfigBuildargs]
        if isinstance(_buildargs, Unset):
            buildargs = UNSET
        else:
            buildargs = ImageBuildConfigBuildargs.from_dict(_buildargs)

        cleanup = d.pop("cleanup", UNSET)

        dockerfile = d.pop("dockerfile", UNSET)

        networks = []
        _networks = d.pop("networks", UNSET)
        for networks_item_data in _networks or []:
            networks_item = EndPointConfig.from_dict(networks_item_data)

            networks.append(networks_item)

        quiet = d.pop("quiet", UNSET)

        tag = d.pop("tag", UNSET)

        image_build_config = cls(
            container_config=container_config,
            context=context,
            buildargs=buildargs,
            cleanup=cleanup,
            dockerfile=dockerfile,
            networks=networks,
            quiet=quiet,
            tag=tag,
        )

        image_build_config.additional_properties = d
        return image_build_config

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
