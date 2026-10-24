import sys
import os
import json
import asyncio

import yaml
import click
import websockets

from .client.models.deployment_config import DeploymentConfig
from .client.models.container_config import ContainerConfig
from .client.api.default.deployment_diff import (
    sync_detailed as deployment_diff_endpoint,
)
from .client.api.default.container_create import (
    sync_detailed as container_create_endpoint,
)
from .client.api.default.network_connect import (
    sync_detailed as network_connect_endpoint,
)
from .client.api.default.network_create import (
    sync_detailed as network_create_endpoint,
)
from .client.api.default.volume_create import (
    sync_detailed as volume_create_endpoint,
)
from .client.api.default.container_list import (
    sync_detailed as container_list_endpoint,
)
from .client.api.default.network_list import (
    sync_detailed as network_list_endpoint,
)
from .client.api.default.volume_list import (
    sync_detailed as volume_list_endpoint,
)
from .connection import create_websocket, request
from .printing import (
    echo,
    echo_bold,
    echo_error,
    group_cls,
    command_cls,
    print_response_msg,
    print_json_raw,
    print_nothing,
    print_backend_error,
    unexpected_error,
    print_bulkbuild_messages,
    connection_closed_unexpectedly,
)
from .utils import request_and_print_response, listen_for_messages
from .container import stop_containers, start_containers, remove_container_list
from .network import remove_network_list
from .volume import remove_volume_list

# pylint: disable=unused-argument

DEFAULT_DEPLOYMENT_FILE = "deployment.yml"
WS_DEPLOY_BUILD_ENDPOINT = "/deployment/build"
DEPLOY_BUILD_START_MESSAGE = "Start building images.."
DEPLOY_BUILD_SUCCEDED = "Succesfully built images."
DEPLOY_BUILD_FAILED = "Failed to build deployment"


@click.group(cls=group_cls())
def root(name="deploy"):
    """Manage deployment"""


def deploy_build(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        # no_args_is_help=True,
        short_help="Build images specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    def build(**kwargs):
        """Build all images defined in the deployment file."""

        deployment_config = _load_deployment_spec(kwargs["file"])
        if not _create_deployment_networks(deployment_config):
            return
        if not _create_deployment_volumes(deployment_config):
            return

        asyncio.run(_build_images_and_listen_for_messages(deployment_config))

    build_options = [
        click.Option(
            ["--file", "-f"],
            default=DEFAULT_DEPLOYMENT_FILE,
            show_default=True,
            help="Specify the deployment file to use.",
        ),
    ]
    build.params.extend(build_options)

    return build


def deploy_create(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Create containers specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    def create(**kwargs):
        """Create the networks, volumes and containers defined in a deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        if not _create_deployment_networks(deployment_config):
            return
        if not _create_deployment_volumes(deployment_config):
            return

        _create_deployment_containers(deployment_config)

    return create


def deploy_remove(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Remove containers related objects specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    @click.option(
        "--volume",
        "-v",
        default=False,
        is_flag=True,
        show_default=True,
        help="Remove any volumes attached to containers",
    )
    @click.option(
        "--force",
        "-F",
        default=False,
        is_flag=True,
        show_default=True,
        help="Do not ask before removing deployment",
    )
    @click.option(
        "--stop",
        "-s",
        default=False,
        is_flag=True,
        show_default=True,
        help="Stop running containers before removing",
    )
    def remove(**kwargs):
        """Remove the containers, networks and volumes defined in a deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        stop = kwargs["stop"]
        force = kwargs["force"]
        remove_volumes = kwargs["volume"]

        if not force:
            click.echo("WARNING! This will remove the specified deployment.")
            click.confirm("Are you sure you want to continue?", abort=True)

        # Remove containers
        echo("Removing containers...")
        container_names = [c.name for c in deployment_config.containers or []]
        remove_container_list(container_names, stop, exit_on_failure=False)

        # Remove network
        echo("Removing networks...")
        network_names = [n.name for n in deployment_config.networks or []]
        remove_network_list(network_names, stop_on_failure=False)

        if remove_volumes:
            echo("Removing volumes...")
            volume_names = [v.name for v in deployment_config.volumes or []]
            remove_volume_list(volume_names, stop_on_failure=False)

    return remove


def deploy_stop(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Stop all containers specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    def stop(**kwargs):
        """Stop all containers defined in the deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        containers = [c.name for c in deployment_config.containers or []]
        stop_containers(containers)

    return stop


def deploy_start(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Start all containers specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    def start(**kwargs):
        """Start all containers defined in the deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        containers = [c.name for c in deployment_config.containers or []]
        detach = True
        interactive = False
        tty = False
        start_containers(detach, interactive, tty, containers)

    return start


def deploy_diff(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Show the difference between a deployment spec and the host.",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    @click.option(
        "--json",
        default=False,
        is_flag=True,
        help="JSON-encode diff result",
    )
    def diff(**kwargs):
        """Show the difference between a deployment file and the state on the host."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        response = request_and_print_response(
            deployment_diff_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: lambda x: None,
                409: print_response_msg,
                404: print_response_msg,
            },
        )

        result_json = response.content.decode("utf8")
        result_json = _adjust_result(result_json)

        if kwargs["json"]:
            print_json_raw(result_json)
        else:
            for line in render_diff(json.loads(result_json)):
                echo(line)

    return diff


def _create_deployment_networks(deployment_config):
    """Create each deployment network via /networks/create.

    A 409 means the name is taken (the network exists from an earlier
    deployment run) and is skipped; any other status fails the deployment.
    """
    for network in deployment_config.networks or []:
        response = request_and_print_response(
            network_create_endpoint,
            kwargs={"json_body": network},
            statuscode2printer={
                201: print_nothing,
                400: print_response_msg,
                409: print_nothing,
                500: print_backend_error,
            },
        )
        if response is None or response.status_code not in (201, 409):
            return False

        if response.status_code == 201:
            echo(f"created network '{network.name}'")

    return True


def _create_deployment_volumes(deployment_config):
    """Create each deployment volume via /volumes/create.

    The endpoint returns the existing volume for a taken name, but the
    deployment flow must stay silent for already-present volumes, so
    existing names are skipped client-side.
    """
    existing = {volume.name for volume in list_volumes()}

    for volume in deployment_config.volumes or []:
        if volume.name in existing:
            continue

        response = request_and_print_response(
            volume_create_endpoint,
            kwargs={"json_body": volume},
            statuscode2printer={201: print_nothing, 500: print_backend_error},
        )
        if response is None or response.status_code != 201:
            return False

        echo(f"created volume '{volume.name}'")

    return True


def _recreate_deployment_containers(deployment_config):
    """Stop and remove every container named in the deployment file so the
    subsequent create rebuilds them from scratch; False on failure.

    Containers that do not exist are tolerated (they are simply created by
    the create step afterwards).
    """
    for container in deployment_config.containers or []:
        echo(f"recreating container '{container.name}'")
        remove_container_list([container.name], force=True, exit_on_failure=False)
    return True


def _create_deployment_containers(deployment_config):
    """Create each deployment container via /containers/create and connect
    its endpoints via /networks/connect; False on failure.

    A 409 means the container name is taken (the container exists from an
    earlier deployment run) and is skipped without connecting it again.
    """
    for container in deployment_config.containers or []:
        response = request_and_print_response(
            container_create_endpoint,
            kwargs={"json_body": container},
            statuscode2printer={
                201: print_nothing,
                404: print_nothing,
                409: print_nothing,
                500: print_nothing,
            },
        )
        if response is None or response.status_code not in (201, 409):
            if response is not None:
                echo_error(
                    f"could not create container '{container.name}': {response.parsed.message}"
                )
            return False

        if response.status_code == 409:
            continue

        container_id = response.parsed.id
        echo(f"created container '{container.name}': {container_id}")

        if not _connect_container_endpoints(container):
            return False

    return True


def _connect_container_endpoints(container):
    """Connect a deployment container to the networks in its endpoints."""
    for endpoint in container.endpoints or []:
        response = request_and_print_response(
            network_connect_endpoint,
            kwargs={"json_body": endpoint},
            statuscode2printer={
                204: print_nothing,
                404: print_response_msg,
                409: print_response_msg,
                500: print_backend_error,
            },
        )
        if response is None or response.status_code != 204:
            if response is not None:
                echo_error(
                    f"could not connect container '{container.name}' "
                    f"to network '{endpoint.network}': {response.parsed.message}"
                )
            return False

    return True


def deploy_up(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Create all objects in a deployment file and start its containers",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    @click.option(
        "--build",
        default=False,
        is_flag=True,
        show_default=True,
        help="Build images before starting containers",
    )
    @click.option(
        "--force-recreate",
        default=False,
        is_flag=True,
        help="Recreate all containers in the deployment file, even if they already exist",
    )
    @click.option(
        "--no-recreate",
        default=False,
        is_flag=True,
        help="Never recreate existing containers, even if their configuration has changed",
    )
    def up(**kwargs):
        """Create all objects in the deployment file and start its containers."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        if kwargs["force_recreate"] and kwargs["no_recreate"]:
            raise click.UsageError("--force-recreate and --no-recreate cannot be used together")
        if not _create_deployment_networks(deployment_config):
            return
        if not _create_deployment_volumes(deployment_config):
            return

        if kwargs["build"]:
            asyncio.run(_build_images_and_listen_for_messages(deployment_config))

        if kwargs["force_recreate"]:
            _recreate_deployment_containers(deployment_config)

        if not _create_deployment_containers(deployment_config):
            return

        containers = [c.name for c in deployment_config.containers or []]
        start_containers(detach=True, interactive=False, tty=False, containers=containers)

    return up


def deploy_down(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Stop and remove all objects in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    @click.option(
        "--volume",
        "-v",
        default=False,
        is_flag=True,
        show_default=True,
        help="Remove volumes as well",
    )
    def down(**kwargs):
        """Stop all containers and remove all objects in the deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        container_names = [c.name for c in deployment_config.containers or []]
        remove_container_list(container_names, force=True, exit_on_failure=False)

        network_names = [n.name for n in deployment_config.networks or []]
        remove_network_list(network_names, stop_on_failure=False)

        if kwargs["volume"]:
            volume_names = [v.name for v in deployment_config.volumes or []]
            remove_volume_list(volume_names, stop_on_failure=False)

    return down


def deploy_restart(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Restart all containers specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    def restart(**kwargs):
        """Restart all containers defined in the deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        containers = [c.name for c in deployment_config.containers or []]
        stop_containers(containers)
        start_containers(detach=True, interactive=False, tty=False, containers=containers)

    return restart


def _list_objects(endpoint, **kwargs):
    """List all objects of a kind via a generated list-endpoint."""
    response = request(endpoint, kwargs=kwargs)
    if response is None:
        sys.exit(1)
    return response.parsed or []


def list_containers():
    return _list_objects(container_list_endpoint, all_=True)


def list_networks():
    return _list_objects(network_list_endpoint)


def list_volumes():
    return _list_objects(volume_list_endpoint)


def deploy_prune(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Remove objects not specified in a deployment file",
    )
    @click.option(
        "--file",
        "-f",
        default=DEFAULT_DEPLOYMENT_FILE,
        show_default=True,
        help="Specify the deployment file to use.",
    )
    def prune(**kwargs):
        """Remove containers, networks and volumes not defined in the deployment file."""
        deployment_config = _load_deployment_spec(kwargs["file"])
        spec_containers = {c.name for c in deployment_config.containers or []}
        spec_networks = {n.name for n in deployment_config.networks or []}
        spec_volumes = {v.name for v in deployment_config.volumes or []}

        for container in list_containers():
            if container.name not in spec_containers:
                remove_container_list([container.id], force=True, exit_on_failure=False)
                echo(f"removed container '{container.name}'")

        for network in list_networks():
            if network.name not in spec_networks:
                remove_network_list([network.name], stop_on_failure=False)
                echo(f"removed network '{network.name}'")

        for volume in list_volumes():
            if volume.name not in spec_volumes:
                remove_volume_list([volume.name], stop_on_failure=False)
                echo(f"removed volume '{volume.name}'")

    return prune


def render_diff(diff):
    """Turn a deployment-diff JSON object into human-readable lines."""
    lines = []
    for kind in ("container", "image", "network", "volume"):
        for name, entries in diff.get(f"{kind}s", {}).items():
            for entry in entries:
                lines.append(_render_diff_entry(kind, name, entry))
    return lines


def _render_diff_entry(kind, name, entry):
    if entry["type"] == "missing_on_host":
        return f"{kind} '{name}' is missing on the host"

    if entry["type"] == "not_equal":
        return (
            f"{kind} '{name}': property '{entry['property']}' differs: "
            f"host={entry['value_host']!r} spec={entry['value_spec']!r}"
        )

    # mountpoint/endpoint/image-specific findings keep their raw repr for now
    return f"{kind} '{name}': {entry}"


def _load_deployment_spec(deployment_path):
    with open(deployment_path, encoding="utf8") as deployment_file:
        deployment_yaml = deployment_file.read()

    deployment = yaml.safe_load(deployment_yaml)
    _add_container_defaults(deployment)
    _add_network_defaults(deployment)
    deployment = DeploymentConfig.from_dict(deployment).to_dict()

    if "images" in deployment:
        for image in deployment["images"]:
            _validate_image_config(image)

            if _is_image_build(image):
                if "context" not in image:
                    image["context"] = "."

                image["context"] = os.path.abspath(image["context"])

                if "container_config" not in image:
                    container_config = ContainerConfig.from_dict(
                        {
                            "name": None,
                            "cmd": None,
                            "network_driver": "host",
                        }
                    ).to_dict()
                    image["container_config"] = container_config

    # This mimics the behavoir of container.py:_create_container_and_connect_to_network
    if "containers" in deployment:
        for container in deployment["containers"]:
            if "network_driver" not in deployment and len(container["endpoints"]) == 0:
                container["network_driver"] = "host"

            if "network_driver" not in deployment and len(container["endpoints"]) > 0:
                container["network_driver"] = "ipnet"

    return DeploymentConfig.from_dict(deployment)


def _validate_image_config(config):
    if "context" in config and "method" in config:
        msg = f"error in image {config['tag']}: both 'context' and 'method' cannot be specified at the same time."
        echo_error(msg)
        sys.exit(1)


def _is_image_build(config):
    return "method" not in config


def _add_network_defaults(deployment):
    if "networks" in deployment:
        for network in deployment["networks"]:
            if "type" not in network:
                network["type"] = "loopback"


def _add_container_defaults(deployment):
    if "containers" in deployment:
        for container in deployment["containers"]:
            if "endpoints" in container:
                for endpoint in container["endpoints"]:
                    endpoint["container"] = container["name"]

                    if "ip_address" not in endpoint and "ip_address6" not in endpoint:
                        endpoint["ip_address"] = "<auto>"
                        endpoint["ip_address6"] = "<auto>"


def _adjust_result(result_json):
    result = json.loads(result_json)
    for _container_name, container_result in result["containers"].items():
        if _nonexisting_image(container_result):
            _remove_user_default_value(container_result)
            _remove_cmd_default_value(container_result)

    result_json = json.dumps(result)
    return result_json


def _nonexisting_image(container_result):
    for entry in container_result:
        if entry["type"] == "non_existing_image":
            return True
    return False


def _remove_user_default_value(container_result):
    for n, entry in enumerate(container_result):
        if (
            entry["type"] == "not_equal"
            and entry["property"] == "user"
            and entry["value_spec"] == ""
        ):
            container_result.pop(n)


def _remove_cmd_default_value(container_result):
    for n, entry in enumerate(container_result):
        if (
            entry["type"] == "not_equal"
            and entry["property"] == "cmd"
            and entry["value_spec"] == []
        ):
            container_result.pop(n)


async def _build_images_and_listen_for_messages(deployment_config):
    deployment_config = json.dumps(deployment_config.to_dict())

    try:
        async with create_websocket(WS_DEPLOY_BUILD_ENDPOINT) as websocket:
            await websocket.send(deployment_config)
            starting_frame = await websocket.recv()
            start_msg = json.loads(starting_frame)
            if start_msg["msg_type"] == "starting":
                echo_bold(DEPLOY_BUILD_START_MESSAGE)
                try:
                    closing_message = await listen_for_messages(
                        websocket, message_processor=print_bulkbuild_messages
                    )
                except json.JSONDecodeError:
                    unexpected_error()
                    sys.exit(1)

                if closing_message["msg_type"] == "error":
                    echo_bold(DEPLOY_BUILD_FAILED)
                    sys.exit(1)

                echo_bold(DEPLOY_BUILD_SUCCEDED)

            elif start_msg["msg_type"] == "error":
                echo_bold(start_msg["message"])
                sys.exit(1)
            else:
                unexpected_error()
                sys.exit(1)

    except websockets.exceptions.ConnectionClosedError:
        connection_closed_unexpectedly()


root.add_command(deploy_build("build"), name="build")
root.add_command(deploy_create("create"), name="create")
root.add_command(deploy_remove("remove"), name="remove")
root.add_command(deploy_stop("stop"), name="stop")
root.add_command(deploy_start("start"), name="start")
root.add_command(deploy_diff("diff"), name="diff")
root.add_command(deploy_up("up"), name="up")
root.add_command(deploy_down("down"), name="down")
root.add_command(deploy_restart("restart"), name="restart")
root.add_command(deploy_prune("prune"), name="prune")
