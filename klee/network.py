import click

from .client.api.default.network_create import sync_detailed as network_create_endpoint
from .client.api.default.network_connect import (
    sync_detailed as network_connect_endpoint,
)
from .client.api.default.network_disconnect import (
    sync_detailed as network_disconnect_endpoint,
)
from .client.api.default.network_list import sync_detailed as network_list_endpoint
from .client.api.default.network_inspect import (
    sync_detailed as network_inspect_endpoint,
)
from .client.api.default.network_remove import sync_detailed as network_remove_endpoint
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
    """Manage networks"""


def network_create(name, hidden=False):
    @root.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
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
        Name of the interface used on the host for the network.
        If not set the interface name is set to 'kleened' postfixed with an integer.
        If `type` is set to 'custom' the value of `interface` must be the name of an existing interface.
      """,
    )
    @click.option("--subnet", default="", help="Subnet in CIDR format for the network")
    @click.option(
        "--subnet6", default="", help="IPv6 subnet in CIDR format for the network"
    )
    @click.option(
        "--gw",
        default="auto",
        help="""VNET+bridge only. The default IPv4 router that is added to 'vnet' containers on startup, if `subnet` is set.
        If set to 'auto' the first IP of `subnet` is added to the bridge and used as a gateway (default).
        Setting `--gw=\"\"` disables adding a gateway.
        """,
    )
    @click.option(
        "--gw6",
        default="auto",
        help="""VNET+bridge only. The default IPv6 router that is added to 'vnet' containers, if `subnet6` is set.
        See `gw` for details.
        """,
    )
    @click.option(
        "--nat",
        default=True,
        metavar="bool",
        help="Whether or not to use NAT for the network's outgoing traffic. Default is to use NAT, use `--no-nat` to disable it.",
    )
    @click.option(
        "--nat-if",
        default=None,
        metavar="string",
        help="""
        Specify which interface to NAT the IPv4 network traffic to.
        Defaults to the host's gateway interface. Ignored if `no-nat` is set.
        """,
    )
    @click.option(
        "--icc",
        default=True,
        metavar="bool",
        show_default=True,
        help="Whether or not to enable connectivity between containers within the same network.",
    )
    @click.option(
        "--internal",
        default=False,
        is_flag=True,
        metavar="flag",
        help="Whether or not the network is internal, i.e., not allowing outgoing upstream traffic",
    )
    @click.argument("name", nargs=1)
    def create(**config):
        """Create a new network."""
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
            network_create_endpoint,
            kwargs={"json_body": network_config},
            statuscode2printer={
                201: print_response_id,
                409: print_response_msg,
                500: print_backend_error,
            },
        )

    return create


def network_remove(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("networks", required=True, nargs=-1)
    def remove(networks):
        """
        Remove one or more networks. Any connected containers will be disconnected.
        """
        for network_id in networks:
            response = request_and_print_response(
                network_remove_endpoint,
                kwargs={"network_id": network_id},
                statuscode2printer={
                    200: print_response_id,
                    404: print_response_msg,
                    500: print_backend_error,
                },
            )
            if response is None or response.status_code != 200:
                break

    return remove


def network_list(name, hidden=False):
    def _print_networks(response):
        networks = [[nw.id, nw.name, nw.type, nw.subnet] for nw in response.parsed]
        print_table(networks, NETWORK_LIST_COLUMNS)

    @click.command(cls=command_cls(), name=name, hidden=hidden)
    def listing():
        """List networks"""
        request_and_print_response(
            network_list_endpoint,
            kwargs={},
            statuscode2printer={200: _print_networks, 500: print_backend_error},
        )

    return listing


def network_inspect(name, hidden=False):
    return inspect_command(
        name=name,
        hidden=hidden,
        argument="network",
        id_var="network_id",
        docs="Display detailed information on a network.",
        endpoint=network_inspect_endpoint,
    )


def network_connect(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.option(
        "--ip",
        default=None,
        help="IPv4 address used for the container. If omitted and a ipv4 subnet exists for **NETWORK**, an unused ip is allocated. Otherwise it is ignored.",
    )
    @click.option(
        "--ip6",
        default=None,
        help="IPv6 address used for the container. If omitted and a ipv6 subnet exists for **NETWORK**, an unused ip is allocated. Otherwise it is ignored.",
    )
    @click.argument("network", required=True, nargs=1)
    @click.argument("container", required=True, nargs=1)
    def connect(ip, ip6, network, container):
        """
        Connect a container to a network.

        **NETWORK** and **CONTAINER** are network and container identifiers, respectively.
        Once connected, the container can communicate with other containers in the same network.
        """
        _connect(ip, ip6, network, container)

    return connect


def network_disconnect(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("network", required=True, nargs=1)
    @click.argument("container", required=True, nargs=1)
    def disconnect(network, container):
        """
        Disconnect a container from a network.

        Running containers can also be disconnected from a network.
        """
        request_and_print_response(
            network_disconnect_endpoint,
            kwargs={"network_id": network, "container_id": container},
            statuscode2printer={
                204: print_nothing,
                404: print_response_msg,
                500: print_backend_error,
            },
        )

    return disconnect


def _connect(ip, ip6, network, container):
    ip = "<auto>" if ip is None else ip
    ip6 = "<auto>" if ip6 is None else ip6

    if ip is not None:
        endpoint_config = EndPointConfig.from_dict(
            {
                "network": network,
                "container": container,
                "ip_address": ip,
                "ip_address6": ip6,
            }
        )
    else:
        endpoint_config = EndPointConfig.from_dict(
            {"network": network, "container": container}
        )

    return request_and_print_response(
        network_connect_endpoint,
        kwargs={"json_body": endpoint_config},
        statuscode2printer={
            204: print_nothing,
            404: print_response_msg,
            409: print_response_msg,
            500: print_backend_error,
        },
    )


root.add_command(network_create("create"), name="create")
root.add_command(network_list("ls"), name="ls")
root.add_command(network_inspect("inspect"), name="inspect")
root.add_command(network_remove("rm"), name="rm")
root.add_command(
    prune_command(
        name="prune",
        docs="Remove all unused networks, i.e., networks without connected containers.",
        warning="WARNING! This will remove all unused networks.",
        endpoint=network_prune_endpoint,
    )
)
root.add_command(network_disconnect("disconnect"), name="disconnect")
root.add_command(network_connect("connect"), name="connect")
