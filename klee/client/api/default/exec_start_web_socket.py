from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.exec_start_config import ExecStartConfig
from ...models.web_socket_message import WebSocketMessage
from ...types import Response


def _get_kwargs(
    *,
    json_body: ExecStartConfig,
) -> Dict[str, Any]:

    pass

    json_json_body = json_body.to_dict()

    return {
        "method": "get",
        "url": "/exec/start",
        "json": json_json_body,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[WebSocketMessage]:
    if response.status_code == HTTPStatus.OK:
        response_200 = WebSocketMessage.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[WebSocketMessage]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport,
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecStartConfig,
    **kwargs,
) -> Response[WebSocketMessage]:
    """exec start

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol used by Kleened
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the protocol frames.
    The specifics of the particular endpoint is described below the generic description of the
    protocol.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the specified request body schema. Thus, the contents of request body should be sent as the
    initial websocket frame instead of being contained in initiating request.

    When the config is received, Kleened sends a 'starting-message' back to the client, indicating
    that Kleened has begun processing the request.
    The starting message, like all protocol messages, follows the schema shown for
    the 200-response below (the WebSocketMessage schema) and has `msg_type` set to `starting`.
    After the starting-message, subsequent frames will be 'raw' output from the running process.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before a starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The starting-message does not have any content.
    * If the exec-instance is started with `attach: false` the starting-message is followed by a
      Close frame with Close Code 1001.
    * When the executed process exits the closing-message in the Close frame tells wether the
      entire container has been stopped or just the exec-instance.

    Args:
        json_body (ExecStartConfig): Options for starting an execution instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebSocketMessage]
    """

    kwargs.update(
        _get_kwargs(
            json_body=json_body,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecStartConfig,
) -> Optional[WebSocketMessage]:
    """exec start

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol used by Kleened
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the protocol frames.
    The specifics of the particular endpoint is described below the generic description of the
    protocol.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the specified request body schema. Thus, the contents of request body should be sent as the
    initial websocket frame instead of being contained in initiating request.

    When the config is received, Kleened sends a 'starting-message' back to the client, indicating
    that Kleened has begun processing the request.
    The starting message, like all protocol messages, follows the schema shown for
    the 200-response below (the WebSocketMessage schema) and has `msg_type` set to `starting`.
    After the starting-message, subsequent frames will be 'raw' output from the running process.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before a starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The starting-message does not have any content.
    * If the exec-instance is started with `attach: false` the starting-message is followed by a
      Close frame with Close Code 1001.
    * When the executed process exits the closing-message in the Close frame tells wether the
      entire container has been stopped or just the exec-instance.

    Args:
        json_body (ExecStartConfig): Options for starting an execution instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebSocketMessage
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecStartConfig,
) -> Response[WebSocketMessage]:
    """exec start

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol used by Kleened
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the protocol frames.
    The specifics of the particular endpoint is described below the generic description of the
    protocol.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the specified request body schema. Thus, the contents of request body should be sent as the
    initial websocket frame instead of being contained in initiating request.

    When the config is received, Kleened sends a 'starting-message' back to the client, indicating
    that Kleened has begun processing the request.
    The starting message, like all protocol messages, follows the schema shown for
    the 200-response below (the WebSocketMessage schema) and has `msg_type` set to `starting`.
    After the starting-message, subsequent frames will be 'raw' output from the running process.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before a starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The starting-message does not have any content.
    * If the exec-instance is started with `attach: false` the starting-message is followed by a
      Close frame with Close Code 1001.
    * When the executed process exits the closing-message in the Close frame tells wether the
      entire container has been stopped or just the exec-instance.

    Args:
        json_body (ExecStartConfig): Options for starting an execution instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebSocketMessage]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecStartConfig,
) -> Optional[WebSocketMessage]:
    """exec start

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol used by Kleened
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the protocol frames.
    The specifics of the particular endpoint is described below the generic description of the
    protocol.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the specified request body schema. Thus, the contents of request body should be sent as the
    initial websocket frame instead of being contained in initiating request.

    When the config is received, Kleened sends a 'starting-message' back to the client, indicating
    that Kleened has begun processing the request.
    The starting message, like all protocol messages, follows the schema shown for
    the 200-response below (the WebSocketMessage schema) and has `msg_type` set to `starting`.
    After the starting-message, subsequent frames will be 'raw' output from the running process.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before a starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The starting-message does not have any content.
    * If the exec-instance is started with `attach: false` the starting-message is followed by a
      Close frame with Close Code 1001.
    * When the executed process exits the closing-message in the Close frame tells wether the
      entire container has been stopped or just the exec-instance.

    Args:
        json_body (ExecStartConfig): Options for starting an execution instance.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebSocketMessage
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
