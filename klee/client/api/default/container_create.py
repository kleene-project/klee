from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.container_config import ContainerConfig
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ContainerConfig,
    name: str,
) -> Dict[str, Any]:
    url = "{}/containers/create".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["name"] = name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[ErrorResponse, IdResponse]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = IdResponse.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(f"Unexpected status code: {response.status_code}")
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[ErrorResponse, IdResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *, client: Client, json_body: ContainerConfig, name: str, **kwargs
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Create a container

    Args:
        name (str):
        json_body (ContainerConfig): Configuration for a container. Some of the configuration
            parameters will overwrite the corresponding parameters in the specified image.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs.update(
        _get_kwargs(
            client=client,
            json_body=json_body,
            name=name,
        )
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    json_body: ContainerConfig,
    name: str,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Create a container

    Args:
        name (str):
        json_body (ContainerConfig): Configuration for a container. Some of the configuration
            parameters will overwrite the corresponding parameters in the specified image.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        name=name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: ContainerConfig,
    name: str,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Create a container

    Args:
        name (str):
        json_body (ContainerConfig): Configuration for a container. Some of the configuration
            parameters will overwrite the corresponding parameters in the specified image.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        name=name,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    json_body: ContainerConfig,
    name: str,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Create a container

    Args:
        name (str):
        json_body (ContainerConfig): Configuration for a container. Some of the configuration
            parameters will overwrite the corresponding parameters in the specified image.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            name=name,
        )
    ).parsed
