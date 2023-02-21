from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.end_point_config import EndPointConfig
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    network_id: str,
    *,
    client: Client,
    json_body: EndPointConfig,
) -> Dict[str, Any]:
    url = "{}/networks/{network_id}/connect".format(
        client.base_url, network_id=network_id
    )

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[Any, ErrorResponse]]:
    if response.status_code == HTTPStatus.NO_CONTENT:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.CONFLICT:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(f"Unexpected status code: {response.status_code}")
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[Any, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    network_id: str,
    *,
    client: Client,
    json_body: EndPointConfig,
) -> Response[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        json_body (EndPointConfig): Configuration of a connection between a network to a
            container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        network_id=network_id,
        client=client,
        json_body=json_body,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    network_id: str,
    *,
    client: Client,
    json_body: EndPointConfig,
) -> Optional[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        json_body (EndPointConfig): Configuration of a connection between a network to a
            container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    return sync_detailed(
        network_id=network_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    network_id: str,
    *,
    client: Client,
    json_body: EndPointConfig,
) -> Response[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        json_body (EndPointConfig): Configuration of a connection between a network to a
            container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        network_id=network_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    network_id: str,
    *,
    client: Client,
    json_body: EndPointConfig,
) -> Optional[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        json_body (EndPointConfig): Configuration of a connection between a network to a
            container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    return (
        await asyncio_detailed(
            network_id=network_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
