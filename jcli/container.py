import asyncio
import json

import click
import websockets

from .client.api.default.container_create import sync_detailed as container_create
from .client.api.default.container_delete import sync_detailed as container_delete
from .client.api.default.container_list import sync_detailed as container_list
from .client.api.default.container_start import sync_detailed as container_start
from .client.api.default.container_stop import sync_detailed as container_stop
from .client.models.container_config import ContainerConfig
from .name_generator import random_name
from .utils import (
    WS_CONTAINER_ATTACH_URL,
    human_duration,
    listen_for_messages,
    request_and_validate_response,
)


# pylint: disable=unused-argument
@click.group()
def root(name="container"):
    """Manage containers"""

@root.command(name="create", context_settings={"ignore_unknown_options": True})
@click.option("--name", default="", help="Assign a name to the container")
@click.option(
    "--network",
    "-n",
    multiple=True,
    default=None,
    help="Connect a container to a network",
)
@click.option(
    "--volume",
    "-v",
    multiple=True,
    default=None,
    help="Bind mount a volume to the container",
)
@click.option(
    "--env",
    "-e",
    multiple=True,
    default=None,
    help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)",
)
@click.option(
    "--jailparam",
    "-J",
    multiple=True,
    default=["mount.devfs"],
    show_default=True,
    help="Specify a jail parameters, see jail(8) for details",
)
@click.argument("image", nargs=1)
@click.argument("command", nargs=-1)
def create(name, network, volume, env, jailparam, image, command):
    """Create a new container"""
    container_config = {
        "cmd": list(command),
        "networks": list(network),
        "volumes": list(volume),
        "image": image,
        "jail_param": list(jailparam),
        "env": list(env),
        "user": "",  # TODO: Should it be possible to override this through cli option?
    }
    container_config = ContainerConfig.from_dict(container_config)
    if name == "":
        name = random_name()

    request_and_validate_response(
        container_create,
        kwargs={"json_body": container_config, "name": name},
        statuscode2messsage={
            201: lambda response: response.parsed.id,
            404: lambda response: response.parsed.message,
            500: lambda response: response.parsed,
        },
    )


@root.command(name="ls")
@click.option(
    "--all",
    "-a",
    default=False,
    is_flag=True,
    help="Show all containers (default shows only running containers)",
)
def list_containers(**kwargs):
    """List containers"""
    request_and_validate_response(
        container_list,
        kwargs={"all_": kwargs["all"]},
        statuscode2messsage={
            200: lambda response: _print_container(response.parsed),
            500: "jocker engine server error",
        },
    )


def _print_container(containers):
    from tabulate import tabulate

    def command_json2command_human(command_str):
        return " ".join(json.loads(command_str))

    def is_running_str(running):
        if running:
            return "running"
        return "stopped"

    headers = ["CONTAINER ID", "IMAGE", "TAG", "COMMAND", "CREATED", "STATUS", "NAME"]
    containers = [
        [
            c.id,
            c.image_id,
            c.image_tag,
            command_json2command_human(c.command),
            human_duration(c.created),
            is_running_str(c.running),
            c.name,
        ]
        for c in containers
    ]

    # TODO: The README.md says that 'maxcolwidths' exists but it complains here. Perhaps it is not in the newest version on pypi yet?
    # col_widths = [12, 15, 23, 18, 7]
    # lines = tabulate(containers, headers=headers,  maxcolwidths=col_widths).split("\n")
    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)


@root.command(name="rm")
@click.argument("containers", required=True, nargs=-1)
def remove(containers):
    """Remove one or more containers"""
    for container_id in containers:
        response = request_and_validate_response(
            container_delete,
            kwargs={"container_id": container_id},
            statuscode2messsage={
                200: lambda response: response.parsed.id,
                404: lambda response: response.parsed.message,
                500: "jocker engine server error",
            },
        )
        if response is None or response.status_code != 200:
            break


@root.command(name="start")
@click.option(
    "--attach", "-a", default=False, is_flag=True, help="Attach to STDOUT/STDERR"
)
@click.argument("containers", required=True, nargs=-1)
def start(attach, containers):
    """Start one or more stopped containers. Attach only if a single container is started"""
    if attach:
        if len(containers) != 1:
            click.echo(
                "only one container can be started when setting the 'attach' flag."
            )
        else:
            _start_attached(containers[0])

    else:
        for container_id in containers:
            response = _start_container(container_id)
            if response is None or response.status_code != 200:
                break


def _start_attached(container_id):
    asyncio.run(_attach_and_start_container(container_id))


async def _attach_and_start_container(container_id):
    endpoint = WS_CONTAINER_ATTACH_URL.format(container_id=container_id)
    async with websockets.connect(endpoint) as websocket:
        hello_msg = await websocket.recv()
        if hello_msg[:3] == "ok:":
            request_and_validate_response(
                container_start,
                kwargs={"container_id": container_id},
                statuscode2messsage={
                    200: lambda response: "",
                    304: lambda response: response.parsed.message,
                    404: lambda response: response.parsed.message,
                    500: "jocker engine server error",
                },
            )
            await listen_for_messages(websocket)
        else:
            click.echo("error attaching to container")


def _start_container(container_id):
    return request_and_validate_response(
        container_start,
        kwargs={"container_id": container_id},
        statuscode2messsage={
            200: lambda response: response.parsed.id,
            304: lambda response: response.parsed.message,
            404: lambda response: response.parsed.message,
            500: "jocker engine server error",
        },
    )


@root.command(name="stop")
@click.argument("containers", nargs=-1)
def stop(containers):
    """Stop one or more running containers"""
    for container_id in containers:
        response = request_and_validate_response(
            container_stop,
            kwargs={"container_id": container_id},
            statuscode2messsage={
                200: lambda response: response.parsed.id,
                304: lambda response: response.parsed.message,
                404: lambda response: response.parsed.message,
                500: "jocker engine server error",
            },
        )
        if response is None or response.status_code != 200:
            break
