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
from .client.api.default.deployment_create_containers import (
    sync_detailed as deployment_create_containers_endpoint,
)
from .client.api.default.deployment_create_networks import (
    sync_detailed as deployment_create_networks_endpoint,
)
from .client.api.default.deployment_create_volumes import (
    sync_detailed as deployment_create_volumes_endpoint,
)
from .connection import create_websocket
from .printing import (
    echo,
    echo_bold,
    echo_error,
    group_cls,
    command_cls,
    print_response_msg,
    print_json_raw,
    unexpected_error,
    print_bulkbuild_messages,
    connection_closed_unexpectedly,
)
from .utils import request_and_print_response, listen_for_messages

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
    def build(**kwargs):
        """
        FIXME: Some useful help-description here.
        """

        deployment_config = _create_deployment(kwargs["file"])
        # Create networks
        response = request_and_print_response(
            deployment_create_networks_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: print_created_networks,
                409: print_response_msg,
                404: print_response_msg,
            },
        )
        if response.status_code != 201:
            return

        # Create volumes
        response = request_and_print_response(
            deployment_create_volumes_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: print_created_volumes,
                409: print_response_msg,
                404: print_response_msg,
            },
        )
        if response.status_code != 201:
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
        """
        FIXME: Some useful help-description here.
        """
        deployment_config = _create_deployment(kwargs["file"])
        # Create networks
        response = request_and_print_response(
            deployment_create_networks_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: print_created_networks,
                409: print_response_msg,
                404: print_response_msg,
            },
        )
        if response.status_code != 201:
            return

        # Create volumes
        response = request_and_print_response(
            deployment_create_volumes_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: print_created_volumes,
                409: print_response_msg,
                404: print_response_msg,
            },
        )
        if response.status_code != 201:
            return

        # Create containers
        request_and_print_response(
            deployment_create_containers_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: print_created_containers,
                409: print_response_msg,
                404: print_response_msg,
            },
        )

    return create


def print_created_containers(response):
    containers = json.loads(response.content)
    for container in containers:
        name = container["name"]
        container_id = container["id"]
        echo(f"created container '{name}': {container_id}")


def print_created_networks(response):
    networks = json.loads(response.content)
    for network in networks:
        name = network["name"]
        echo(f"created network '{name}'")


def print_created_volumes(response):
    volumes = json.loads(response.content)
    for volume in volumes:
        name = volume["name"]
        echo(f"created volume '{name}'")


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
        """
        FIXME: Some useful help-description here.
        """
        deployment_config = _create_deployment(kwargs["file"])
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
            echo_bold("Implement me!")

    return diff


def _create_deployment(deployment_path):
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
root.add_command(deploy_diff("diff"), name="diff")
