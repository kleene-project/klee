from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.image_labels import ImageLabels


T = TypeVar("T", bound="Image")


@_attrs_define
class Image:
    """the image metadata

    Attributes:
        cmd (Union[Unset, List[str]]): Default command used when creating a container from this image Example:
            ['/bin/sh', '-c', '/bin/ls'].
        created (Union[Unset, str]): When the image was created
        dataset (Union[Unset, str]): ZFS dataset of the image
        digest (Union[Unset, None, str]): Digest of the image manifest (OCI images). Default: ''.
        entrypoint (Union[Unset, None, List[str]]): Entrypoint of the image (OCI images). Prepended to `cmd` when
            starting a container.
        env (Union[Unset, List[str]]): Environment variables and their values to set before running command. Example:
            ['PWD=/roo/', 'JAIL_MGMT_ENGINE=kleene'].
        id (Union[Unset, str]): The id of the image
        instructions (Union[Unset, List[List[str]]]): Instructions and their corresponding snapshots (if they exist)
            that were used to build the image.
            Each item in the array consists of a 2-element array `["<instruction>","<snapshot>"]`
            containing one instruction and possibly its snapshot.
            The latter is only be present with `RUN` or `COPY` instructions that ran succesfully.
            Otherwise `<snapshot>` is empty.
        labels (Union[Unset, None, ImageLabels]): Labels of the image (OCI images).
        name (Union[Unset, str]): Name of the image
        source (Union[Unset, str]): Where the image came from: `"build"` or `"oci"`. Default: 'build'.
        tag (Union[Unset, str]): Tag of the image
        user (Union[Unset, str]): User used for running `cmd`
        workdir (Union[Unset, None, str]): Working directory of the image (OCI images). Default: ''.
    """

    cmd: Union[Unset, List[str]] = UNSET
    created: Union[Unset, str] = UNSET
    dataset: Union[Unset, str] = UNSET
    digest: Union[Unset, None, str] = ""
    entrypoint: Union[Unset, None, List[str]] = UNSET
    env: Union[Unset, List[str]] = UNSET
    id: Union[Unset, str] = UNSET
    instructions: Union[Unset, List[List[str]]] = UNSET
    labels: Union[Unset, None, "ImageLabels"] = UNSET
    name: Union[Unset, str] = UNSET
    source: Union[Unset, str] = "build"
    tag: Union[Unset, str] = UNSET
    user: Union[Unset, str] = UNSET
    workdir: Union[Unset, None, str] = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cmd: Union[Unset, List[str]] = UNSET
        if not isinstance(self.cmd, Unset):
            cmd = self.cmd

        created = self.created
        dataset = self.dataset
        digest = self.digest
        entrypoint: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.entrypoint, Unset):
            if self.entrypoint is None:
                entrypoint = None
            else:
                entrypoint = self.entrypoint

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

        labels: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict() if self.labels else None

        name = self.name
        source = self.source
        tag = self.tag
        user = self.user
        workdir = self.workdir

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cmd is not UNSET:
            field_dict["cmd"] = cmd
        if created is not UNSET:
            field_dict["created"] = created
        if dataset is not UNSET:
            field_dict["dataset"] = dataset
        if digest is not UNSET:
            field_dict["digest"] = digest
        if entrypoint is not UNSET:
            field_dict["entrypoint"] = entrypoint
        if env is not UNSET:
            field_dict["env"] = env
        if id is not UNSET:
            field_dict["id"] = id
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if labels is not UNSET:
            field_dict["labels"] = labels
        if name is not UNSET:
            field_dict["name"] = name
        if source is not UNSET:
            field_dict["source"] = source
        if tag is not UNSET:
            field_dict["tag"] = tag
        if user is not UNSET:
            field_dict["user"] = user
        if workdir is not UNSET:
            field_dict["workdir"] = workdir

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.image_labels import ImageLabels

        d = src_dict.copy()
        cmd = cast(List[str], d.pop("cmd", UNSET))

        created = d.pop("created", UNSET)

        dataset = d.pop("dataset", UNSET)

        digest = d.pop("digest", UNSET)

        entrypoint = cast(List[str], d.pop("entrypoint", UNSET))

        env = cast(List[str], d.pop("env", UNSET))

        id = d.pop("id", UNSET)

        instructions = []
        _instructions = d.pop("instructions", UNSET)
        for instructions_item_data in _instructions or []:
            instructions_item = cast(List[str], instructions_item_data)

            instructions.append(instructions_item)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, None, ImageLabels]
        if _labels is None:
            labels = None
        elif isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = ImageLabels.from_dict(_labels)

        name = d.pop("name", UNSET)

        source = d.pop("source", UNSET)

        tag = d.pop("tag", UNSET)

        user = d.pop("user", UNSET)

        workdir = d.pop("workdir", UNSET)

        image = cls(
            cmd=cmd,
            created=created,
            dataset=dataset,
            digest=digest,
            entrypoint=entrypoint,
            env=env,
            id=id,
            instructions=instructions,
            labels=labels,
            name=name,
            source=source,
            tag=tag,
            user=user,
            workdir=workdir,
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
