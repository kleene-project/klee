import click

from .client.api.default.network_connect import sync_detailed as network_connect
from .client.api.default.network_create import sync_detailed as network_create
from .client.api.default.network_disconnect import sync_detailed as network_disconnect
from .client.api.default.network_list import sync_detailed as network_list
from .client.api.default.network_remove import sync_detailed as network_remove
from .client.models.network_config import NetworkConfig
from .utils import request_and_validate_response


# pylint: disable=unused-argument
@click.group()
def root(name="network"):
    """Manage networks"""


@root.command(name="create")
@click.option(
    "--driver",
    "-d",
    default="loopback",
    show_default=True,
    help="Which driver to use for the network. 'vnet' or 'loopback' is possible. See the networking documentation for details.",
)
@click.option(
    "--ifname",
    required=True,
    help="Name of the loopback interface used for the network",
)
@click.option("--subnet", required=True, help="Subnet in CIDR format for the network")
@click.argument("network_name", nargs=1)
def create(driver, ifname, subnet, network_name):
    """Create a new network"""
    network_config = {
        "name": network_name,
        "ifname": ifname,
        "subnet": subnet,
        "driver": driver,
    }

    network_config = NetworkConfig.from_dict(network_config)

    request_and_validate_response(
        network_create,
        kwargs={"json_body": network_config},
        statuscode2messsage={
            201: lambda response: response.parsed.id,
            409: lambda response: response.parsed.message,
            500: "jocker engine server error",
        },
    )


@root.command(name="rm")
@click.argument("networks", required=True, nargs=-1)
def remove(networks):
    """Remove one or more networks."""
    for network_id in networks:
        response = request_and_validate_response(
            network_remove,
            kwargs={"network_id": network_id},
            statuscode2messsage={
                200: lambda response: response.parsed.id,
                404: lambda response: response.parsed.message,
                500: "jocker engine server error",
            },
        )
        if response is None or response.status_code != 200:
            break


@root.command(name="ls")
def list_networks():
    """List networks"""
    request_and_validate_response(
        network_list,
        kwargs={},
        statuscode2messsage={
            200: lambda response: _print_networks(response.parsed),
            500: "jocker engine server error",
        },
    )


def _print_networks(networks):
    from tabulate import tabulate

    headers = ["ID", "NAME", "DRIVER", "SUBNET"]
    containers = [[nw.id, nw.name, nw.driver, nw.subnet] for nw in networks]

    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)


@root.command(name="connect")
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def connect(network, container):
    """Connect a container to a network"""
    request_and_validate_response(
        network_connect,
        kwargs={"network_id": network, "container_id": container},
        statuscode2messsage={
            204: "OK",
            404: lambda response: response.parsed.message,
            409: lambda response: response.parsed.message,
            500: "jocker engine server error",
        },
    )


@root.command(name="disconnect")
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def disconnect(network, container):
    """Disconnect a container to a network"""
    request_and_validate_response(
        network_disconnect,
        kwargs={"network_id": network, "container_id": container},
        statuscode2messsage={
            204: "OK",
            404: lambda response: response.parsed.message,
            500: "jocker engine server error",
        },
    )
