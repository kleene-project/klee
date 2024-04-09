from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.container_config import ContainerConfig
from ...models.error_response import ErrorResponse
from ...models.id_response import IdResponse
from ...types import Response


def _get_kwargs(
    container_id: str,
    *,
    json_body: ContainerConfig,
) -> Dict[str, Any]:

    pass

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": "/containers/{container_id}/update".format(
            container_id=container_id,
        ),
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
    if response.status_code == HTTPStatus.CONFLICT:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409
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
    container_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ContainerConfig,
    **kwargs,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """container update

     Re-configure a container.

    The JSON request body is identical to [Container.Create](#operation/Container.Create),
    and is being interpreted as follows:

    - The `image` property is ignored.
    - All other properties will replace the existing ones, if they are not `null`.

    Some of the changes might require a running container to be restarted.

    Args:
        container_id (str):
        json_body (ContainerConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs.update(
        _get_kwargs(
            container_id=container_id,
            json_body=json_body,
        )
    )

    client = httpx.Client(base_url=client._base_url, transport=transport)
    response = client.request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    container_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ContainerConfig,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """container update

     Re-configure a container.

    The JSON request body is identical to [Container.Create](#operation/Container.Create),
    and is being interpreted as follows:

    - The `image` property is ignored.
    - All other properties will replace the existing ones, if they are not `null`.

    Some of the changes might require a running container to be restarted.

    Args:
        container_id (str):
        json_body (ContainerConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return sync_detailed(
        container_id=container_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    container_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ContainerConfig,
) -> Response[Union[ErrorResponse, IdResponse]]:
    """container update

     Re-configure a container.

    The JSON request body is identical to [Container.Create](#operation/Container.Create),
    and is being interpreted as follows:

    - The `image` property is ignored.
    - All other properties will replace the existing ones, if they are not `null`.

    Some of the changes might require a running container to be restarted.

    Args:
        container_id (str):
        json_body (ContainerConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, IdResponse]]
    """

    kwargs = _get_kwargs(
        container_id=container_id,
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    container_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: ContainerConfig,
) -> Optional[Union[ErrorResponse, IdResponse]]:
    """container update

     Re-configure a container.

    The JSON request body is identical to [Container.Create](#operation/Container.Create),
    and is being interpreted as follows:

    - The `image` property is ignored.
    - All other properties will replace the existing ones, if they are not `null`.

    Some of the changes might require a running container to be restarted.

    Args:
        container_id (str):
        json_body (ContainerConfig):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, IdResponse]
    """

    return (
        await asyncio_detailed(
            container_id=container_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
