from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.web_socket_message_msg_type import WebSocketMessageMsgType

T = TypeVar("T", bound="WebSocketMessage")


@_attrs_define
class WebSocketMessage:
    """Protocol messages sent from Kleened's websocket endpoints

    Example:
        {'data': '', 'message': 'succesfully started execution instance in detached mode', 'msg_type': 'closing'}

    Attributes:
        data (str): Any data that might have been created by the process such as an image ID. Default: ''.
        message (str): A useful message to tell the client what has happened. Default: ''.
        msg_type (WebSocketMessageMsgType): Which type of message.
    """

    msg_type: WebSocketMessageMsgType
    data: str = ""
    message: str = ""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.data
        message = self.message
        msg_type = self.msg_type.value

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

        msg_type = WebSocketMessageMsgType(d.pop("msg_type"))

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
