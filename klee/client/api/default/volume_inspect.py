from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.volume_inspect import VolumeInspect
from ...types import Response


def _get_kwargs(
    volume_name: str,
) -> Dict[str, Any]:

    pass

    return {
        "method": "get",
        "url": "/volumes/{volume_name}/inspect".format(
            volume_name=volume_name,
        ),
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, VolumeInspect]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = VolumeInspect.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, VolumeInspect]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport, volume_name: str, *, client: Union[AuthenticatedClient, Client], **kwargs
) -> Response[Union[ErrorResponse, VolumeInspect]]:
    """volume inspect

     Inspect a volume and its mountpoints.

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, VolumeInspect]]
    """

    kwargs.update(
        _get_kwargs(
            volume_name=volume_name,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    volume_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[ErrorResponse, VolumeInspect]]:
    """volume inspect

     Inspect a volume and its mountpoints.

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, VolumeInspect]
    """

    return sync_detailed(
        volume_name=volume_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    volume_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[ErrorResponse, VolumeInspect]]:
    """volume inspect

     Inspect a volume and its mountpoints.

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, VolumeInspect]]
    """

    kwargs = _get_kwargs(
        volume_name=volume_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    volume_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[ErrorResponse, VolumeInspect]]:
    """volume inspect

     Inspect a volume and its mountpoints.

    Args:
        volume_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, VolumeInspect]
    """

    return (
        await asyncio_detailed(
            volume_name=volume_name,
            client=client,
        )
    ).parsed
