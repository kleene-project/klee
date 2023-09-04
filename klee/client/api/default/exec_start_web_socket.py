from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.exec_start_config import ExecStartConfig
from ...models.web_socket_message import WebSocketMessage
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ExecStartConfig,
) -> Dict[str, Any]:
    url = "{}/exec/start".format(client.base_url)

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
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = WebSocketMessage.from_dict(response.json())

        return response_400
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
    transport, *, client: Client, json_body: ExecStartConfig, **kwargs
) -> Response[WebSocketMessage]:
    """exec start

     make a description of the websocket endpoint here.

    Args:
        json_body (ExecStartConfig): Options for starting an execution instance.

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
    json_body: ExecStartConfig,
) -> Optional[WebSocketMessage]:
    """exec start

     make a description of the websocket endpoint here.

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
    client: Client,
    json_body: ExecStartConfig,
) -> Response[WebSocketMessage]:
    """exec start

     make a description of the websocket endpoint here.

    Args:
        json_body (ExecStartConfig): Options for starting an execution instance.

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
    json_body: ExecStartConfig,
) -> Optional[WebSocketMessage]:
    """exec start

     make a description of the websocket endpoint here.

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
