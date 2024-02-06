from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.network_inspect import NetworkInspect
from ...types import Response


def _get_kwargs(
    network_id: str,
) -> Dict[str, Any]:

    pass

    return {
        "method": "get",
        "url": "/networks/{network_id}/inspect".format(
            network_id=network_id,
        ),
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, NetworkInspect]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = NetworkInspect.from_dict(response.json())

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
) -> Response[Union[ErrorResponse, NetworkInspect]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport, network_id: str, *, client: Union[AuthenticatedClient, Client], **kwargs
) -> Response[Union[ErrorResponse, NetworkInspect]]:
    """network inspect

     Inspect a network and its endpoints.

    Args:
        network_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, NetworkInspect]]
    """

    kwargs.update(
        _get_kwargs(
            network_id=network_id,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    network_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[ErrorResponse, NetworkInspect]]:
    """network inspect

     Inspect a network and its endpoints.

    Args:
        network_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, NetworkInspect]
    """

    return sync_detailed(
        network_id=network_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    network_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[ErrorResponse, NetworkInspect]]:
    """network inspect

     Inspect a network and its endpoints.

    Args:
        network_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, NetworkInspect]]
    """

    kwargs = _get_kwargs(
        network_id=network_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    network_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[ErrorResponse, NetworkInspect]]:
    """network inspect

     Inspect a network and its endpoints.

    Args:
        network_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, NetworkInspect]
    """

    return (
        await asyncio_detailed(
            network_id=network_id,
            client=client,
        )
    ).parsed
