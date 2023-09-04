from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="WebSocketMessage")


@attr.s(auto_attribs=True)
class WebSocketMessage:
    """The request have been validated and the request is being processed.

    Attributes:
        data (str): Any data that might have been created in pre-processing (e.g., a build_id). Default: ''.
        message (str): Any data that might have been created in pre-processing (e.g., a build_id). Default: ''.
        msg_type (str): Any data that might have been created in pre-processing (e.g., a build_id).
    """

    msg_type: str
    data: str = ""
    message: str = ""
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.data
        message = self.message
        msg_type = self.msg_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "message": message,
                "msg_type": msg_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data = d.pop("data")

        message = d.pop("message")

        msg_type = d.pop("msg_type")

        web_socket_message = cls(
            data=data,
            message=message,
            msg_type=msg_type,
        )

        web_socket_message.additional_properties = d
        return web_socket_message

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
