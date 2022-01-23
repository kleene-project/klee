from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...models.volume_config import VolumeConfig
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: VolumeConfig,
) -> Dict[str, Any]:
    url = "{}/volumes/create".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[ErrorResponse, IdResponse]]:
    if response.status_code == 201:
        response_201 = IdResponse.from_dict(response.json())

        return response_201
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
    *,
    client: Client,
    json_body: VolumeConfig,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Create a volume

    Args:
        json_body (VolumeConfig): Volume configuration

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: VolumeConfig,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Create a volume

    Args:
        json_body (VolumeConfig): Volume configuration

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: VolumeConfig,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Create a volume

    Args:
        json_body (VolumeConfig): Volume configuration

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: VolumeConfig,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Create a volume

    Args:
        json_body (VolumeConfig): Volume configuration

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
