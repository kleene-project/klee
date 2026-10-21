from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_object import ErrorObject
from ...models.error_response import ErrorResponse
from ...models.network import Network
from ...models.network_config import NetworkConfig
from ...types import Response


def _get_kwargs(
    *,
    json_body: List["NetworkConfig"],
) -> Dict[str, Any]:

    pass

    json_json_body = []
    for componentsschemas_network_config_list_item_data in json_body:
        componentsschemas_network_config_list_item = (
            componentsschemas_network_config_list_item_data.to_dict()
        )

        json_json_body.append(componentsschemas_network_config_list_item)

    return {
        "method": "post",
        "url": "/networks/create",
        "json": json_json_body,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, List[Union["ErrorObject", "Network"]]]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = []
        _response_201 = response.json()
        for componentsschemas_network_create_result_item_data in _response_201:

            def _parse_componentsschemas_network_create_result_item(
                data: object,
            ) -> Union["ErrorObject", "Network"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_network_create_result_item_type_0 = (
                        Network.from_dict(data)
                    )

                    return componentsschemas_network_create_result_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_network_create_result_item_type_1 = (
                    ErrorObject.from_dict(data)
                )

                return componentsschemas_network_create_result_item_type_1

            componentsschemas_network_create_result_item = (
                _parse_componentsschemas_network_create_result_item(
                    componentsschemas_network_create_result_item_data
                )
            )

            response_201.append(componentsschemas_network_create_result_item)

        return response_201
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, List[Union["ErrorObject", "Network"]]]]:
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
    json_body: List["NetworkConfig"],
    **kwargs,
) -> Response[Union[ErrorResponse, List[Union["ErrorObject", "Network"]]]]:
    """network create

     Create one or more networks from a list of configurations.

    Args:
        json_body (List['NetworkConfig']): List of network configurations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, List[Union['ErrorObject', 'Network']]]]
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
    json_body: List["NetworkConfig"],
) -> Optional[Union[ErrorResponse, List[Union["ErrorObject", "Network"]]]]:
    """network create

     Create one or more networks from a list of configurations.

    Args:
        json_body (List['NetworkConfig']): List of network configurations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, List[Union['ErrorObject', 'Network']]]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: List["NetworkConfig"],
) -> Response[Union[ErrorResponse, List[Union["ErrorObject", "Network"]]]]:
    """network create

     Create one or more networks from a list of configurations.

    Args:
        json_body (List['NetworkConfig']): List of network configurations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, List[Union['ErrorObject', 'Network']]]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    json_body: List["NetworkConfig"],
) -> Optional[Union[ErrorResponse, List[Union["ErrorObject", "Network"]]]]:
    """network create

     Create one or more networks from a list of configurations.

    Args:
        json_body (List['NetworkConfig']): List of network configurations.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, List[Union['ErrorObject', 'Network']]]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
