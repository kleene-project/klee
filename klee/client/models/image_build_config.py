from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_build_config_buildargs import ImageBuildConfigBuildargs


T = TypeVar("T", bound="ImageBuildConfig")


@attr.s(auto_attribs=True)
class ImageBuildConfig:
    """make a description of the websocket endpoint here.

    Attributes:
        context (str): description here
        buildargs (Union[Unset, ImageBuildConfigBuildargs]): Object of string pairs for build-time variables. Users pass
            these values at build-time. Kleened uses the buildargs as the environment context for commands run via the
            Dockerfile RUN instruction, or for variable expansion in other Dockerfile instructions. This is not meant for
            passing secret values. Example: {'JAIL_MGMT_ENGINE': 'kleene', 'USERNAME': 'Stephen'}.
        cleanup (Union[Unset, bool]): description here Default: True.
        dockerfile (Union[Unset, str]): description here Default: 'Dockerfile'.
        quiet (Union[Unset, bool]): description here
        tag (Union[Unset, str]): description here Default: ''.
    """

    context: str
    buildargs: Union[Unset, "ImageBuildConfigBuildargs"] = UNSET
    cleanup: Union[Unset, bool] = True
    dockerfile: Union[Unset, str] = "Dockerfile"
    quiet: Union[Unset, bool] = False
    tag: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context = self.context
        buildargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.buildargs, Unset):
            buildargs = self.buildargs.to_dict()

        cleanup = self.cleanup
        dockerfile = self.dockerfile
        quiet = self.quiet
        tag = self.tag

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "context": context,
            }
        )
        if buildargs is not UNSET:
            field_dict["buildargs"] = buildargs
        if cleanup is not UNSET:
            field_dict["cleanup"] = cleanup
        if dockerfile is not UNSET:
            field_dict["dockerfile"] = dockerfile
        if quiet is not UNSET:
            field_dict["quiet"] = quiet
        if tag is not UNSET:
            field_dict["tag"] = tag

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.image_build_config_buildargs import ImageBuildConfigBuildargs

        d = src_dict.copy()
        context = d.pop("context")

        _buildargs = d.pop("buildargs", UNSET)
        buildargs: Union[Unset, ImageBuildConfigBuildargs]
        if isinstance(_buildargs, Unset):
            buildargs = UNSET
        else:
            buildargs = ImageBuildConfigBuildargs.from_dict(_buildargs)

        cleanup = d.pop("cleanup", UNSET)

        dockerfile = d.pop("dockerfile", UNSET)

        quiet = d.pop("quiet", UNSET)

        tag = d.pop("tag", UNSET)

        image_build_config = cls(
            context=context,
            buildargs=buildargs,
            cleanup=cleanup,
            dockerfile=dockerfile,
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
