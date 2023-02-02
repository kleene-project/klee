from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.container_summary import ContainerSummary
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    all_: Union[Unset, None, bool] = UNSET,
) -> Dict[str, Any]:
    url = "{}/containers/list".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["all"] = all_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[List[ContainerSummary]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_container_summary_list_item_data in _response_200:
            componentsschemas_container_summary_list_item = ContainerSummary.from_dict(
                componentsschemas_container_summary_list_item_data
            )

            response_200.append(componentsschemas_container_summary_list_item)

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[List[ContainerSummary]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    all_: Union[Unset, None, bool] = UNSET,
) -> Response[List[ContainerSummary]]:
    """List containers

     Returns a compact listing of containers.

    Args:
        all_ (Union[Unset, None, bool]):

    Returns:
        Response[List[ContainerSummary]]
    """

    kwargs = _get_kwargs(
        client=client,
        all_=all_,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    all_: Union[Unset, None, bool] = UNSET,
) -> Optional[List[ContainerSummary]]:
    """List containers

     Returns a compact listing of containers.

    Args:
        all_ (Union[Unset, None, bool]):

    Returns:
        Response[List[ContainerSummary]]
    """

    return sync_detailed(
        client=client,
        all_=all_,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    all_: Union[Unset, None, bool] = UNSET,
) -> Response[List[ContainerSummary]]:
    """List containers

     Returns a compact listing of containers.

    Args:
        all_ (Union[Unset, None, bool]):

    Returns:
        Response[List[ContainerSummary]]
    """

    kwargs = _get_kwargs(
        client=client,
        all_=all_,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    all_: Union[Unset, None, bool] = UNSET,
) -> Optional[List[ContainerSummary]]:
    """List containers

     Returns a compact listing of containers.

    Args:
        all_ (Union[Unset, None, bool]):

    Returns:
        Response[List[ContainerSummary]]
    """

    return (
        await asyncio_detailed(
            client=client,
            all_=all_,
        )
    ).parsed
