from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.image_build_config import ImageBuildConfig
from ...models.web_socket_message import WebSocketMessage
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ImageBuildConfig,
) -> Dict[str, Any]:
    url = "{}/images/build".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[WebSocketMessage]:
    if response.status_code == HTTPStatus.OK:
        response_200 = WebSocketMessage.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(f"Unexpected status code: {response.status_code}")
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[WebSocketMessage]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport, *, client: Client, json_body: ImageBuildConfig, **kwargs
) -> Response[WebSocketMessage]:
    r"""image build

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the websocket protocol messages.
    The specifics of the particular endpoint is described below the general description.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the request body below. Thus, the contents of request body should be sent as the initial
    frame instead of being contained in the request body.

    When the config is received, a starting-message is returned, indicating that the process has
    started. The starting message, like all protocol messages, follows the schema shown for
    the 200-response (the WebSocketMessage schema).
    After the starting-message, subsequent frames will be 'raw' output from the particular
    process being started.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is always set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before the starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The `data` field in the starting-message contains the `image_id`.
    * If the build process is successful, the `data` field in the closing-message contains the
    `image_id` otherwise it contains the latest snapshot or empty string `\"\"` if the build failed
    before any snapshots have been created.

    Args:
        json_body (ImageBuildConfig): Configuration for an image build.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebSocketMessage
    """

    kwargs.update(
        _get_kwargs(
            client=client,
            json_body=json_body,
        )
    )

    cookies = kwargs.pop("cookies")
    client = httpx.Client(transport=transport, cookies=cookies)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    json_body: ImageBuildConfig,
) -> Optional[WebSocketMessage]:
    r"""image build

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the websocket protocol messages.
    The specifics of the particular endpoint is described below the general description.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the request body below. Thus, the contents of request body should be sent as the initial
    frame instead of being contained in the request body.

    When the config is received, a starting-message is returned, indicating that the process has
    started. The starting message, like all protocol messages, follows the schema shown for
    the 200-response (the WebSocketMessage schema).
    After the starting-message, subsequent frames will be 'raw' output from the particular
    process being started.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is always set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before the starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The `data` field in the starting-message contains the `image_id`.
    * If the build process is successful, the `data` field in the closing-message contains the
    `image_id` otherwise it contains the latest snapshot or empty string `\"\"` if the build failed
    before any snapshots have been created.

    Args:
        json_body (ImageBuildConfig): Configuration for an image build.

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
    client: Client,
    json_body: ImageBuildConfig,
) -> Response[WebSocketMessage]:
    r"""image build

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the websocket protocol messages.
    The specifics of the particular endpoint is described below the general description.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the request body below. Thus, the contents of request body should be sent as the initial
    frame instead of being contained in the request body.

    When the config is received, a starting-message is returned, indicating that the process has
    started. The starting message, like all protocol messages, follows the schema shown for
    the 200-response (the WebSocketMessage schema).
    After the starting-message, subsequent frames will be 'raw' output from the particular
    process being started.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is always set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before the starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The `data` field in the starting-message contains the `image_id`.
    * If the build process is successful, the `data` field in the closing-message contains the
    `image_id` otherwise it contains the latest snapshot or empty string `\"\"` if the build failed
    before any snapshots have been created.

    Args:
        json_body (ImageBuildConfig): Configuration for an image build.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebSocketMessage
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    json_body: ImageBuildConfig,
) -> Optional[WebSocketMessage]:
    r"""image build

     > **Important**: This is a 'dummy' specification since the actual endpoint is websocket-based.
    > Below is a description of the websocket protocol and how it relates to the dummy spec.

    ## General websocket protocol
    All of Kleened's websocket endpoints follows a similar pattern, having only differences
    in the contents of the fields in the websocket protocol messages.
    The specifics of the particular endpoint is described below the general description.

    Once the websocket is established, Kleened expects a configuration-frame, which is given by
    the request body below. Thus, the contents of request body should be sent as the initial
    frame instead of being contained in the request body.

    When the config is received, a starting-message is returned, indicating that the process has
    started. The starting message, like all protocol messages, follows the schema shown for
    the 200-response (the WebSocketMessage schema).
    After the starting-message, subsequent frames will be 'raw' output from the particular
    process being started.
    When the process is finished, Kleened closes the websocket with a Close Code 1000 and a
    WebSocketMessage contained in the Close frame's Close Reason.
    The `msg_type` is always set to `closing` but the contents of the `data` and `message` fields
    depend on the particular endpoint.

    If the initial configuration message schema is invalid, kleened closes the websocket with
    Close Code 1002 and a WebSocketMessage as the Close frame's Close Reason.
    The `msg_type` is set to `error` and the contents of the `data` and `message` fields will
    depend on the specific error.
    This only happens before the starting-message have been sent to the client.

    If Kleened encounters an error during process execution, Kleened closes the websocket with
    Close Code 1011 and a WebSocketMessage as the Close frame's reason. The `msg_type` is set to
    `error` and the contents of the `data` and `message` fields will depend on the specific error.

    If any unexpected errors/crashes occur during the lifetime of the websocket, Kleend closes
    the websocket with Close Code 1011 and an empty reason field.

    ## Endpoint-specific details
    The following specifics pertain to this endpoint:


    * The `data` field in the starting-message contains the `image_id`.
    * If the build process is successful, the `data` field in the closing-message contains the
    `image_id` otherwise it contains the latest snapshot or empty string `\"\"` if the build failed
    before any snapshots have been created.

    Args:
        json_body (ImageBuildConfig): Configuration for an image build.

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
