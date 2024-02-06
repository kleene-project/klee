from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response


def _get_kwargs(
    *,
    all_: bool,
) -> Dict[str, Any]:

    pass

    params: Dict[str, Any] = {}
    params["all"] = all_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "post",
        "url": "/images/prune",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List[str]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = cast(List[str], response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List[str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport, *, client: Union[AuthenticatedClient, Client], all_: bool, **kwargs
) -> Response[List[str]]:
    """image prune

     Remove images that are not being used by containers.

    Args:
        all_ (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List[str]]
    """

    kwargs.update(
        _get_kwargs(
            all_=all_,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    all_: bool,
) -> Optional[List[str]]:
    """image prune

     Remove images that are not being used by containers.

    Args:
        all_ (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List[str]
    """

    return sync_detailed(
        client=client,
        all_=all_,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    all_: bool,
) -> Response[List[str]]:
    """image prune

     Remove images that are not being used by containers.

    Args:
        all_ (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List[str]]
    """

    kwargs = _get_kwargs(
        all_=all_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    all_: bool,
) -> Optional[List[str]]:
    """image prune

     Remove images that are not being used by containers.

    Args:
        all_ (bool):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List[str]
    """

    return (
        await asyncio_detailed(
            client=client,
            all_=all_,
        )
    ).parsed
