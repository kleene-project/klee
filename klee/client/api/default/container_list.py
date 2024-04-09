from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.container_summary import ContainerSummary
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    all_: Union[Unset, None, bool] = UNSET,
) -> Dict[str, Any]:

    pass

    params: Dict[str, Any] = {}
    params["all"] = all_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/containers/list",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["ContainerSummary"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_container_summary_list_item_data in _response_200:
            componentsschemas_container_summary_list_item = ContainerSummary.from_dict(
                componentsschemas_container_summary_list_item_data
            )

            response_200.append(componentsschemas_container_summary_list_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["ContainerSummary"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    transport,
    *,
    client: Union[AuthenticatedClient, Client],
    all_: Union[Unset, None, bool] = UNSET,
    **kwargs,
) -> Response[List["ContainerSummary"]]:
    """container list

     Returns a list of container summaries. For detailed information about a container,
    use [Container.Inspect](#operation/Container.Inspect).

    Args:
        all_ (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ContainerSummary']]
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
    all_: Union[Unset, None, bool] = UNSET,
) -> Optional[List["ContainerSummary"]]:
    """container list

     Returns a list of container summaries. For detailed information about a container,
    use [Container.Inspect](#operation/Container.Inspect).

    Args:
        all_ (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ContainerSummary']
    """

    return sync_detailed(
        client=client,
        all_=all_,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    all_: Union[Unset, None, bool] = UNSET,
) -> Response[List["ContainerSummary"]]:
    """container list

     Returns a list of container summaries. For detailed information about a container,
    use [Container.Inspect](#operation/Container.Inspect).

    Args:
        all_ (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ContainerSummary']]
    """

    kwargs = _get_kwargs(
        all_=all_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    all_: Union[Unset, None, bool] = UNSET,
) -> Optional[List["ContainerSummary"]]:
    """container list

     Returns a list of container summaries. For detailed information about a container,
    use [Container.Inspect](#operation/Container.Inspect).

    Args:
        all_ (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ContainerSummary']
    """

    return (
        await asyncio_detailed(
            client=client,
            all_=all_,
        )
    ).parsed
