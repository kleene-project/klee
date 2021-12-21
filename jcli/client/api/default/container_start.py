from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import Response


def _get_kwargs(
    container_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/containers/{container_id}/start".format(
        client.base_url, container_id=container_id
    )

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
    if response.status_code == 304:
        response_304 = ErrorResponse.from_dict(response.json())

        return response_304
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
    container_id: str,
    *,
    client: Client,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Start a container

    Args:
        container_id (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        container_id=container_id,
        client=client,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    container_id: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Start a container

    Args:
        container_id (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return sync_detailed(
        container_id=container_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    container_id: str,
    *,
    client: Client,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Start a container

    Args:
        container_id (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        container_id=container_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    container_id: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Start a container

    Args:
        container_id (str):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return (
        await asyncio_detailed(
            container_id=container_id,
            client=client,
        )
    ).parsed
