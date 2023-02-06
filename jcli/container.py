import asyncio
import json
import urllib

import click
import websockets

from .client.api.default.container_create import sync_detailed as container_create
from .client.api.default.container_list import sync_detailed as container_list
from .client.api.default.container_remove import sync_detailed as container_remove
from .client.api.default.container_stop import sync_detailed as container_stop
from .client.api.default.exec_create import sync_detailed as exec_create
from .client.models.container_config import ContainerConfig
from .client.models.exec_config import ExecConfig
from .name_generator import random_name
from .utils import (
    WS_EXEC_START_URL,
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
    "--user",
    "-u",
    default="",
    help="Alternate user that should be used for starting the container",
)
@click.option("--network", "-n", default=None, help="Connect a container to a network")
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
    "--ip",
    default=None,
    help="IPv4 address (e.g., 172.30.100.104). If the '--network' parameter is not set '--ip' is ignored.",
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
def create(name, user, network, volume, env, ip, jailparam, image, command):
    """Create a new container"""
    if network is not None:
        if ip is not None:
            network = {network: {"container": "dummy", "ip_address": ip}}
        else:
            network = {network: {"container": "dummy"}}
    else:
        network = {}

    container_config = {
        "cmd": list(command),
        "networks": network,
        "volumes": list(volume),
        "image": image,
        "jail_param": list(jailparam),
        "env": list(env),
        "user": user,
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

    # NOTE: The README.md says that 'maxcolwidths' exists but it complains here.
    # Perhaps it is not in the newest version on pypi yet? col_widths = [12,15,23,18,7]
    # lines = tabulate(containers, headers=headers, maxcolwidths=col_widths).split("\n")
    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)


@root.command(name="rm")
@click.argument("containers", required=True, nargs=-1)
def remove(containers):
    """Remove one or more containers"""
    for container_id in containers:
        response = request_and_validate_response(
            container_remove,
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
    """Start one or more stopped containers.
    Attach only if a single container is started
    """
    if attach:
        if len(containers) != 1:
            click.echo(
                "only one container can be started when setting the 'attach' flag."
            )
        else:
            start_attached_container(containers[0])

    else:
        for container_id in containers:
            start_container(container_id)


def start_attached_container(container_id):
    asyncio.run(_attach_and_start_container(container_id))


def start_container(container_id):
    asyncio.run(_start_container(container_id))


async def _attach_and_start_container(container_id):
    response = _create_exec_instance(container_id)

    if response.status_code == 201:
        click.echo(f"created execution instance {response.parsed.id}")
        exec_id = response.parsed.id
        endpoint = WS_EXEC_START_URL.format(
            exec_id=exec_id,
            options=urllib.parse.urlencode(
                {"attach": "true", "start_container": "true"}
            ),
        )

        async with websockets.connect(endpoint) as websocket:
            hello_msg = await websocket.recv()
            if hello_msg == "OK":
                await listen_for_messages(websocket)
            elif hello_msg[:6] == "ERROR:":
                click.echo(hello_msg[6:])
                await listen_for_messages(websocket)
            else:
                click.echo("error starting container #{container_id}")
    else:
        click.echo(
            f"{container_id}: error creating execution instance: {response.parsed}"
        )


async def _start_container(container_id):
    response = _create_exec_instance(container_id)
    if response.status_code == 201:
        click.echo(f"created execution instance {response.parsed.id}")
        exec_id = response.parsed.id
        endpoint = WS_EXEC_START_URL.format(
            exec_id=exec_id,
            options=urllib.parse.urlencode(
                {"attach": "false", "start_container": "true"}
            ),
        )

        async with websockets.connect(endpoint) as websocket:
            await websocket.wait_closed()
            if websocket.close_code != 1001:
                click.echo("error starting container #{container_id}")
    else:
        click.echo(
            f"{container_id}: error creating execution instance: {response.parsed}"
        )


def _create_exec_instance(container_id):
    exec_config = ExecConfig.from_dict(
        {"container_id": container_id, "cmd": [], "env": [], "user": ""}
    )
    response = request_and_validate_response(
        exec_create,
        kwargs={"json_body": exec_config},
        statuscode2messsage={
            201: lambda response: "",
            404: lambda response: response.parsed.message,
            500: lambda response: response.parsed,
        },
    )
    return response


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
