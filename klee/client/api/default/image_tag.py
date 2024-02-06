from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import UNSET, Response


def _get_kwargs(
    image_id: str,
    *,
    nametag: str,
) -> Dict[str, Any]:

    pass

    params: Dict[str, Any] = {}
    params["nametag"] = nametag

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "post",
        "url": "/images/{image_id}/tag".format(
            image_id=image_id,
        ),
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
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
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, IdResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport,
    image_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nametag: str,
    **kwargs,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """image tag

     Update the tag of an image.

    Args:
        image_id (str):
        nametag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs.update(
        _get_kwargs(
            image_id=image_id,
            nametag=nametag,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    image_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nametag: str,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """image tag

     Update the tag of an image.

    Args:
        image_id (str):
        nametag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return sync_detailed(
        image_id=image_id,
        client=client,
        nametag=nametag,
    ).parsed


async def asyncio_detailed(
    image_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nametag: str,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """image tag

     Update the tag of an image.

    Args:
        image_id (str):
        nametag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        image_id=image_id,
        nametag=nametag,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    image_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    nametag: str,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """image tag

     Update the tag of an image.

    Args:
        image_id (str):
        nametag (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return (
        await asyncio_detailed(
            image_id=image_id,
            client=client,
            nametag=nametag,
        )
    ).parsed
