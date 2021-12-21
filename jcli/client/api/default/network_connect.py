from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    network_id: str,
    container_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/networks/{network_id}/connect/{container_id}".format(
        client.base_url, network_id=network_id, container_id=container_id
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, ErrorResponse]]:
    if response.status_code == 204:
        response_204 = None

        return response_204
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, ErrorResponse]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    network_id: str,
    container_id: str,
    *,
    client: Client,
) -> Response[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        container_id (str):

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        network_id=network_id,
        container_id=container_id,
        client=client,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    network_id: str,
    container_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        container_id (str):

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    return sync_detailed(
        network_id=network_id,
        container_id=container_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    network_id: str,
    container_id: str,
    *,
    client: Client,
) -> Response[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        container_id (str):

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        network_id=network_id,
        container_id=container_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    network_id: str,
    container_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, ErrorResponse]]:
    """Connect a container to a network

    Args:
        network_id (str):
        container_id (str):

    Returns:
        Response[Union[Any, ErrorResponse]]
    """

    return (
        await asyncio_detailed(
            network_id=network_id,
            container_id=container_id,
            client=client,
        )
    ).parsed
