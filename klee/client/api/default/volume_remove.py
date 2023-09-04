from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import Response


def _get_kwargs(
    volume_name: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/volumes/{volume_name}".format(client.base_url, volume_name=volume_name)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "delete",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[ErrorResponse, IdResponse]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = IdResponse.from_dict(response.json())

        return response_200
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
    transport, volume_name: str, *, client: Client, **kwargs
) -> Response[Union[ErrorResponse, IdResponse]]:
    """volume remove

     Remove a volume

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    kwargs.update(
        _get_kwargs(
            volume_name=volume_name,
            client=client,
        )
    )

    cookies = kwargs.pop("cookies")
    client = httpx.Client(transport=transport, cookies=cookies)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    volume_name: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """volume remove

     Remove a volume

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return sync_detailed(
        volume_name=volume_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    volume_name: str,
    *,
    client: Client,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """volume remove

     Remove a volume

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    kwargs = _get_kwargs(
        volume_name=volume_name,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume_name: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """volume remove

     Remove a volume

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return (
        await asyncio_detailed(
            volume_name=volume_name,
            client=client,
        )
    ).parsed
