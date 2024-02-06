from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.exec_config import ExecConfig
from ...models.id_response import IdResponse
from ...types import Response


def _get_kwargs(
    *,
    json_body: ExecConfig,
) -> Dict[str, Any]:

    pass

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": "/exec/create",
        "json": json_json_body,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, IdResponse]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = IdResponse.from_dict(response.json())

        return response_201
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
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecConfig,
    **kwargs,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """exec create

     Create an execution instance within a container.

    Args:
        json_body (ExecConfig): Configuration of an executable to run within a container. Some of
            the configuration parameters will overwrite the corresponding parameters if they are
            defined in the container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs.update(
        _get_kwargs(
            json_body=json_body,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecConfig,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """exec create

     Create an execution instance within a container.

    Args:
        json_body (ExecConfig): Configuration of an executable to run within a container. Some of
            the configuration parameters will overwrite the corresponding parameters if they are
            defined in the container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecConfig,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """exec create

     Create an execution instance within a container.

    Args:
        json_body (ExecConfig): Configuration of an executable to run within a container. Some of
            the configuration parameters will overwrite the corresponding parameters if they are
            defined in the container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ExecConfig,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """exec create

     Create an execution instance within a container.

    Args:
        json_body (ExecConfig): Configuration of an executable to run within a container. Some of
            the configuration parameters will overwrite the corresponding parameters if they are
            defined in the container.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
