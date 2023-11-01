from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_buildargs import ImageBuildargs


T = TypeVar("T", bound="Image")


@_attrs_define
class Image:
    """the image metadata

    Attributes:
        buildargs (Union[Unset, ImageBuildargs]): Object of string pairs for build-time variables. Users pass these
            values at build-time. Kleened uses the buildargs as the environment context for commands run via the Dockerfile
            RUN instruction, or for variable expansion in other Dockerfile instructions. This is not meant for passing
            secret values. Example: {'JAIL_MGMT_ENGINE': 'kleene', 'USERNAME': 'Stephen'}.
        command (Union[Unset, List[str]]): Default command used when creating a container from this image Example:
            ['/bin/sh', '-c', '/bin/ls'].
        created (Union[Unset, str]): When the image was created
        env (Union[Unset, List[str]]): Environment variables and their values to set before running command. Example:
            ['PWD=/roo/', 'JAIL_MGMT_ENGINE=kleene'].
        id (Union[Unset, str]): The id of the image
        instructions (Union[Unset, List[List[str]]]): Instructions and their corresponding snapshots, if any, used for
            creating the image.
            Each item in the array is comprised of a 2-element array of the form `["<instruction>","<snapshot>"]`
            containing a instruction and its snapshot.
            The latter will only be present if it is a `RUN` or `COPY` instruction that executed succesfully.
            Otherwise `<snapshot>` will be an empty string.
        layer_id (Union[Unset, str]): Id of the layer containing the image
        name (Union[Unset, str]): Name of the image
        tag (Union[Unset, str]): Tag of the image
        user (Union[Unset, str]): user used when executing the command
    """

    buildargs: Union[Unset, "ImageBuildargs"] = UNSET
    command: Union[Unset, List[str]] = UNSET
    created: Union[Unset, str] = UNSET
    env: Union[Unset, List[str]] = UNSET
    id: Union[Unset, str] = UNSET
    instructions: Union[Unset, List[List[str]]] = UNSET
    layer_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    tag: Union[Unset, str] = UNSET
    user: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        buildargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.buildargs, Unset):
            buildargs = self.buildargs.to_dict()

        command: Union[Unset, List[str]] = UNSET
        if not isinstance(self.command, Unset):
            command = self.command

        created = self.created
        env: Union[Unset, List[str]] = UNSET
        if not isinstance(self.env, Unset):
            env = self.env

        id = self.id
        instructions: Union[Unset, List[List[str]]] = UNSET
        if not isinstance(self.instructions, Unset):
            instructions = []
            for instructions_item_data in self.instructions:
                instructions_item = instructions_item_data

                instructions.append(instructions_item)

        layer_id = self.layer_id
        name = self.name
        tag = self.tag
        user = self.user

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if buildargs is not UNSET:
            field_dict["buildargs"] = buildargs
        if command is not UNSET:
            field_dict["command"] = command
        if created is not UNSET:
            field_dict["created"] = created
        if env is not UNSET:
            field_dict["env"] = env
        if id is not UNSET:
            field_dict["id"] = id
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
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
        from ..models.image_buildargs import ImageBuildargs

        d = src_dict.copy()
        _buildargs = d.pop("buildargs", UNSET)
        buildargs: Union[Unset, ImageBuildargs]
        if isinstance(_buildargs, Unset):
            buildargs = UNSET
        else:
            buildargs = ImageBuildargs.from_dict(_buildargs)

        command = cast(List[str], d.pop("command", UNSET))

        created = d.pop("created", UNSET)

        env = cast(List[str], d.pop("env", UNSET))

        id = d.pop("id", UNSET)

        instructions = []
        _instructions = d.pop("instructions", UNSET)
        for instructions_item_data in _instructions or []:
            instructions_item = cast(List[str], instructions_item_data)

            instructions.append(instructions_item)

        layer_id = d.pop("layer_id", UNSET)

        name = d.pop("name", UNSET)

        tag = d.pop("tag", UNSET)

        user = d.pop("user", UNSET)

        image = cls(
            buildargs=buildargs,
            command=command,
            created=created,
            env=env,
            id=id,
            instructions=instructions,
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
