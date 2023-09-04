from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ExecStartConfig")


@attr.s(auto_attribs=True)
class ExecStartConfig:
    """Options for starting an execution instance.

    Attributes:
        attach (bool): Whether to receive output from `stdin` and `stderr`.
        exec_id (str): id of the execution instance to start
        start_container (bool): Whether to start the container if it is not running.
    """

    attach: bool
    exec_id: str
    start_container: bool
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        attach = self.attach
        exec_id = self.exec_id
        start_container = self.start_container

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attach": attach,
                "exec_id": exec_id,
                "start_container": start_container,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        attach = d.pop("attach")

        exec_id = d.pop("exec_id")

        start_container = d.pop("start_container")

        exec_start_config = cls(
            attach=attach,
            exec_id=exec_id,
            start_container=start_container,
        )

        exec_start_config.additional_properties = d
        return exec_start_config

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
