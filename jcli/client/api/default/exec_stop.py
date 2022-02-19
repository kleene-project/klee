from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import UNSET, Response


def _get_kwargs(
    exec_id: str,
    *,
    client: Client,
    force_stop: bool,
    stop_container: bool,
) -> Dict[str, Any]:
    url = "{}/exec/{exec_id}/stop".format(client.base_url, exec_id=exec_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "force_stop": force_stop,
        "stop_container": stop_container,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[ErrorResponse, IdResponse]]:
    if response.status_code == 200:
        response_200 = IdResponse.from_dict(response.json())

        return response_200
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
    exec_id: str,
    *,
    client: Client,
    force_stop: bool,
    stop_container: bool,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Stop and/or destroy a execution instance.

    Args:
        exec_id (str):
        force_stop (bool):
        stop_container (bool):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        exec_id=exec_id,
        client=client,
        force_stop=force_stop,
        stop_container=stop_container,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    exec_id: str,
    *,
    client: Client,
    force_stop: bool,
    stop_container: bool,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Stop and/or destroy a execution instance.

    Args:
        exec_id (str):
        force_stop (bool):
        stop_container (bool):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return sync_detailed(
        exec_id=exec_id,
        client=client,
        force_stop=force_stop,
        stop_container=stop_container,
    ).parsed


async def asyncio_detailed(
    exec_id: str,
    *,
    client: Client,
    force_stop: bool,
    stop_container: bool,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """Stop and/or destroy a execution instance.

    Args:
        exec_id (str):
        force_stop (bool):
        stop_container (bool):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        exec_id=exec_id,
        client=client,
        force_stop=force_stop,
        stop_container=stop_container,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    exec_id: str,
    *,
    client: Client,
    force_stop: bool,
    stop_container: bool,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """Stop and/or destroy a execution instance.

    Args:
        exec_id (str):
        force_stop (bool):
        stop_container (bool):

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    return (
        await asyncio_detailed(
            exec_id=exec_id,
            client=client,
            force_stop=force_stop,
            stop_container=stop_container,
        )
    ).parsed
