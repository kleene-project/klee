import click

from .client.api.default.network_connect import sync_detailed as network_connect
from .client.api.default.network_create import sync_detailed as network_create
from .client.api.default.network_disconnect import sync_detailed as network_disconnect
from .client.api.default.network_list import sync_detailed as network_list_endpoint
from .client.api.default.network_inspect import (
    sync_detailed as network_inspect_endpoint,
)
from .client.api.default.network_remove import sync_detailed as network_remove
from .client.api.default.network_prune import sync_detailed as network_prune_endpoint

from .client.models.end_point_config import EndPointConfig
from .client.models.network_config import NetworkConfig

from .printing import (
    print_table,
    group_cls,
    command_cls,
    print_response_id,
    print_response_msg,
    print_backend_error,
    print_nothing,
)
from .prune import prune_command
from .inspect import inspect_command
from .utils import request_and_print_response

NETWORK_LIST_COLUMNS = [
    ("ID", {"style": "cyan"}),
    ("NAME", {"style": "bold aquamarine1"}),
    ("TYPE", {"style": "bright_white"}),
    ("SUBNET", {"style": "bold aquamarine1"}),
]

# pylint: disable=unused-argument
@click.group(cls=group_cls(), add_help_option=True, short_help="Manage networks")
def root(name="network"):
    """Manage networks using the following `subcommands`."""


@root.command(cls=command_cls(), name="create", no_args_is_help=True)
@click.option(
    "--type",
    "-t",
    default="loopback",
    show_default=True,
    help="What kind of network should be created. Possible values are 'bridge', 'loopback', and 'custom'.",
)
@click.option(
    "--interface",
    "-i",
    default="",
    help="""
    Name of the interface used for the host interface of the network.
    If not set the interface name is set to `kleened` postfixed with an integer.
    If the `type` is set to `custom` the value of `interface` must be the name of an existing interface.
  """,
)
@click.option("--subnet", default="", help="Subnet in CIDR format for the network")
@click.option(
    "--subnet6", default="", help="IPv6 subnet in CIDR format for the network"
)
@click.option(
    "--gw",
    default="auto",
    help="""The default IPv4 router that is added to 'vnet' containers, if `--subnet` is set.
    Only affects bridge networks. Set `--gw=auto` to use the same gateway as the host (default).
    Setting `--gw=\"\"` implies that no gateway is used.
    """,
)
@click.option(
    "--gw6",
    default="auto",
    help="""The default IPv6 router that is added to 'vnet' containers, if `--subnet6` is set.
    See `--gw` for details.
    """,
)
@click.option(
    "--nat",
    default=True,
    is_flag=True,
    help="Whether or not to use NAT for networks outgoing traffic. Default is to use NAT, use `--no-nat` to disable it.",
)
@click.option(
    "--nat-if",
    default=None,
    help="""
    Specify which interface to NAT the IPv4 network traffic to.
    Defaults to the host's gateway interface. Ignored if `--no-nat` is set.
    """,
)
@click.option(
    "--icc",
    default=True,
    is_flag=True,
    help="Whether or not to enable connectivity between containers within the same network.",
)
@click.option(
    "--internal",
    default=False,
    is_flag=True,
    help="Whether or not the network is internal, i.e., not allowing outgoing upstream traffic",
)
@click.argument("name", nargs=1)
def create(**config):
    """Create a new network named **NAME**."""
    config["gateway"] = config.pop("gw")
    config["gateway6"] = config.pop("gw6")
    for gw in ["gateway", "gateway6"]:
        config[gw] = "<auto>" if config[gw] == "auto" else config[gw]

    nat = config.pop("nat")
    nat_interface = config.pop("nat_if")
    if nat:
        config["nat"] = "<host-gateway>" if nat_interface is None else nat_interface
    else:
        config["nat"] = ""

    network_config = NetworkConfig.from_dict(config)

    request_and_print_response(
        network_create,
        kwargs={"json_body": network_config},
        statuscode2printer={
            201: print_response_id,
            409: print_response_msg,
            500: print_backend_error,
        },
    )


@root.command(cls=command_cls(), name="rm", no_args_is_help=True)
@click.argument("networks", required=True, nargs=-1)
def remove(networks):
    """
    Remove one or more networks. Any connected containers will be disconnected.
    """
    for network_id in networks:
        response = request_and_print_response(
            network_remove,
            kwargs={"network_id": network_id},
            statuscode2printer={
                200: print_response_id,
                404: print_response_msg,
                500: print_backend_error,
            },
        )
        if response is None or response.status_code != 200:
            break


root.add_command(
    prune_command(
        name="prune",
        docs="Remove all unused networks, i.e., networks without connected containers.",
        warning="WARNING! This will remove all unused networks.",
        endpoint=network_prune_endpoint,
    )
)


def network_list(name, hidden=False):
    def _print_networks(response):
        networks = [[nw.id, nw.name, nw.type, nw.subnet] for nw in response.parsed]
        print_table(networks, NETWORK_LIST_COLUMNS)

    @root.command(cls=command_cls(), name=name, hidden=hidden)
    def listing():
        """List networks"""
        request_and_print_response(
            network_list_endpoint,
            kwargs={},
            statuscode2printer={200: _print_networks, 500: print_backend_error},
        )

    return listing


root.add_command(network_list("ls"), name="ls")


root.add_command(
    inspect_command(
        name="inspect",
        argument="network",
        id_var="network_id",
        docs="Display detailed information on a network.",
        endpoint=network_inspect_endpoint,
    ),
    name="inspect",
)


@root.command(cls=command_cls(), name="connect", no_args_is_help=True)
@click.option(
    "--ip",
    default=None,
    help="Specify an IPv4 address used for the container. If `--ip` is omitted and a (ipv4) subnet exists for **NETWORK**, an unused ip is allocated from it. Otherwise it is ignored.",
)
@click.option(
    "--ip6",
    default=None,
    help="Specify an IPv6 address used for the container. If `--ip6` is omitted and a (ipv6) subnet exists for **NETWORK**, an unused ip is allocated from it. Otherwise it is ignored.",
)
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def connect(ip, ip6, network, container):
    """
    Connect a container to a network.

    You can connect a container by name or by ID.
    Once connected, the container can communicate with other containers in
    the same network.
    """
    _connect(ip, ip6, network, container)


def _connect(ip, ip6, network, container):
    ip = "<auto>" if ip is None else ip
    ip6 = "<auto>" if ip6 is None else ip6

    if ip is not None:
        endpoint_config = EndPointConfig.from_dict(
            {"container": container, "ip_address": ip, "ip_address6": ip6}
        )
    else:
        endpoint_config = EndPointConfig.from_dict({"container": container})

    return request_and_print_response(
        network_connect,
        kwargs={"network_id": network, "json_body": endpoint_config},
        statuscode2printer={
            204: print_nothing,
            404: print_response_msg,
            409: print_response_msg,
            500: print_backend_error,
        },
    )


@root.command(cls=command_cls(), name="disconnect", no_args_is_help=True)
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def disconnect(network, container):
    """
    Disconnect a container from a network.

    The container must be stopped before it can be disconnected.
    """
    request_and_print_response(
        network_disconnect,
        kwargs={"network_id": network, "container_id": container},
        statuscode2printer={
            204: print_nothing,
            404: print_response_msg,
            500: print_backend_error,
        },
    )
