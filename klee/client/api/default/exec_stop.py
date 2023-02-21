from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
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

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["force_stop"] = force_stop

    params["stop_container"] = stop_container

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
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
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        exec_id=exec_id,
        client=client,
        force_stop=force_stop,
        stop_container=stop_container,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

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
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


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

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

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
