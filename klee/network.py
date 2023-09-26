import click

from .client.api.default.network_connect import sync_detailed as network_connect
from .client.api.default.network_create import sync_detailed as network_create
from .client.api.default.network_disconnect import sync_detailed as network_disconnect
from .client.api.default.network_list import sync_detailed as network_list
from .client.api.default.network_remove import sync_detailed as network_remove
from .client.models.end_point_config import EndPointConfig
from .client.models.network_config import NetworkConfig

from .utils import (
    request_and_validate_response,
    console,
    print_table,
    KLEE_MSG,
    CONNECTION_CLOSED_UNEXPECTEDLY,
    UNEXPECTED_ERROR,
)

IFNAME_NEEDED_FOR_LOOPBACK_DRIVER = KLEE_MSG.format(
    msg="Option 'ifname' is needed when the network driver 'loopback' is used"
)
NETWORK_LIST_COLUMNS = [
    ("ID", {"style": "cyan"}),
    ("NAME", {"style": "bold aquamarine1"}),
    ("DRIVER", {"style": "bright_white"}),
    ("SUBNET", {"style": "bold aquamarine1"}),
]

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
    help="Which driver to use for the network. Possible values are 'vnet', 'loopback', and 'host'. See jails(8) and the networking documentation for details.",
)
@click.option(
    "--ifname",
    default="",
    help="Name of the loopback interface used for the loopback network",
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
    if driver == "loopback" and ifname is None:
        console.print(IFNAME_NEEDED_FOR_LOOPBACK_DRIVER)

    else:
        network_config = NetworkConfig.from_dict(network_config)

        request_and_validate_response(
            network_create,
            kwargs={"json_body": network_config},
            statuscode2messsage={
                201: lambda response: response.parsed.id,
                409: lambda response: response.parsed.message,
                500: "kleened backend error",
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
                500: "kleened backend error",
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
            500: "kleened backend error",
        },
    )


def _print_networks(networks):
    networks = [[nw.id, nw.name, nw.driver, nw.subnet] for nw in networks]
    print_table(networks, NETWORK_LIST_COLUMNS)


@root.command(name="connect")
@click.option(
    "--ip",
    default=None,
    help="IPv4 address (e.g., 172.30.100.104) used for the container.",
)
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def connect(ip, network, container):
    """Connect a container to a network"""
    connect_(ip, network, container)


def connect_(ip, network, container):
    if ip is not None:
        endpoint_config = EndPointConfig.from_dict(
            {"container": container, "ip_address": ip}
        )
    else:
        endpoint_config = EndPointConfig.from_dict({"container": container})

    return request_and_validate_response(
        network_connect,
        kwargs={"network_id": network, "json_body": endpoint_config},
        statuscode2messsage={
            204: "OK",
            404: lambda response: response.parsed.message,
            409: lambda response: response.parsed.message,
            500: "kleened backend error",
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
            500: "kleened backend error",
        },
    )
