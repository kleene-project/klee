from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_config import DeploymentConfig
from ...models.error_response import ErrorResponse
from ...models.volume import Volume
from ...types import Response


def _get_kwargs(
    *,
    json_body: DeploymentConfig,
) -> Dict[str, Any]:

    pass

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": "/deployment/create/volumes",
        "json": json_json_body,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, List["Volume"]]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = []
        _response_201 = response.json()
        for componentsschemas_volume_list_item_data in _response_201:
            componentsschemas_volume_list_item = Volume.from_dict(
                componentsschemas_volume_list_item_data
            )

            response_201.append(componentsschemas_volume_list_item)

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
) -> Response[Union[ErrorResponse, List["Volume"]]]:
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
    json_body: DeploymentConfig,
    **kwargs,
) -> Response[Union[ErrorResponse, List["Volume"]]]:
    """create deployment volumes

     Create deployment volumes.

    Args:
        json_body (DeploymentConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, List['Volume']]]
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
    json_body: DeploymentConfig,
) -> Optional[Union[ErrorResponse, List["Volume"]]]:
    """create deployment volumes

     Create deployment volumes.

    Args:
        json_body (DeploymentConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, List['Volume']]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: DeploymentConfig,
) -> Response[Union[ErrorResponse, List["Volume"]]]:
    """create deployment volumes

     Create deployment volumes.

    Args:
        json_body (DeploymentConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, List['Volume']]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: DeploymentConfig,
) -> Optional[Union[ErrorResponse, List["Volume"]]]:
    """create deployment volumes

     Create deployment volumes.

    Args:
        json_body (DeploymentConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, List['Volume']]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
