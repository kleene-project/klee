from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import Response


def _get_kwargs(
    image_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/images/{image_id}".format(client.base_url, image_id=image_id)

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
    transport, image_id: str, *, client: Client, **kwargs
) -> Response[Union[ErrorResponse, IdResponse]]:
    """image remove

     Remove an image.

    Images can't be removed if they have descendant images or are being
    used by a running container.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    kwargs.update(
        _get_kwargs(
            image_id=image_id,
            client=client,
        )
    )

    cookies = kwargs.pop("cookies")
    client = httpx.Client(transport=transport, cookies=cookies)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    image_id: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """image remove

     Remove an image.

    Images can't be removed if they have descendant images or are being
    used by a running container.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return sync_detailed(
        image_id=image_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    image_id: str,
    *,
    client: Client,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """image remove

     Remove an image.

    Images can't be removed if they have descendant images or are being
    used by a running container.

    Args:
        image_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    kwargs = _get_kwargs(
        image_id=image_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    image_id: str,
    *,
    client: Client,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """image remove

     Remove an image.

    Images can't be removed if they have descendant images or are being
    used by a running container.

    Args:
        image_id (str):

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
        )
    ).parsed
