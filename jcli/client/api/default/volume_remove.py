from typing import Any, Dict, Optional, Union

import httpx

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

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[ErrorResponse, IdResponse]]:
    if response.status_code == 200:
        response_200 = IdResponse.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[ErrorResponse, IdResponse]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    volume_name: str,
    *,
    client: Client,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Remove a volume

    Args:
        volume_name (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        volume_name=volume_name,
        client=client,
    )

    response = httpx.delete(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    volume_name: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Remove a volume

    Args:
        volume_name (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
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
    """Remove a volume

    Args:
        volume_name (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        volume_name=volume_name,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)


async def asyncio(
    volume_name: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Remove a volume

    Args:
        volume_name (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return (
        await asyncio_detailed(
            volume_name=volume_name,
            client=client,
        )
    ).parsed
