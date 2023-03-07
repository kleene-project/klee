import sys
import asyncio
import json
import urllib
import functools
import signal


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
@click.option("--network", "-n", default=None, help="Connect a container to a network.")
@click.option(
    "--ip",
    default=None,
    help="IPv4 address (e.g., 172.30.100.104). If the '--network' parameter is not set '--ip' is ignored.",
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
    default=["mount.devfs", 'exec.stop="/bin/sh /etc/rc.shutdown jail"'],
    show_default=True,
    help="Specify a jail parameters, see jail(8) for details",
)
@click.argument("image", nargs=1)
@click.argument("command", nargs=-1)
def create(name, user, network, ip, volume, env, jailparam, image, command):
    """Create a new container"""
    create_(name, user, network, ip, volume, env, jailparam, image, command)


def create_(name, user, network, ip, volume, env, jailparam, image, command):
    if network is not None:
        if ip is not None:
            network = {network: {"container": "dummy", "ip_address": ip}}
        else:
            network = {network: {"container": "dummy"}}
    else:
        network = {}

    if volume is None:
        volumes = []
    else:
        volumes = list(volume)

    container_config = {
        "cmd": list(command),
        "networks": network,
        "volumes": volumes,
        "image": image,
        "jail_param": list(jailparam),
        "env": list(env),
        "user": user,
    }
    container_config = ContainerConfig.from_dict(container_config)
    if name == "":
        name = random_name()

    return request_and_validate_response(
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
            500: "kleened backend error",
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
                500: "kleened backend error",
            },
        )
        if response is None or response.status_code != 200:
            break


@root.command(name="start")
@click.option(
    "--attach", "-a", default=False, is_flag=True, help="Attach to STDOUT/STDERR"
)
@click.option(
    "--interactive",
    "-i",
    default=False,
    is_flag=True,
    help="Send terminal input to container's STDIN. Ignored if '--attach' is not used.",
)
@click.option("--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY")
@click.argument("containers", required=True, nargs=-1)
def start(attach, interactive, tty, containers):
    """Start one or more stopped containers.
    Attach only if a single container is started
    """
    start_(attach, interactive, tty, containers)


def start_(attach, interactive, tty, containers):
    if attach:
        if len(containers) != 1:
            click.echo(
                "only one container can be started when setting the 'attach' flag."
            )
        else:
            container = containers[0]
            if interactive:
                _start_interactive_container(container, tty)
            else:
                _start_attached_container(container, tty)

    else:
        if len(containers) == 1:
            start_container(containers[0], tty)
        else:
            for container_id in containers:
                start_container(container_id)


def _start_attached_container(container_id, tty):
    exec_id = _create_exec_instance(container_id, tty)
    endpoint = _build_endpoint(exec_id)
    if exec_id is not None:
        asyncio.run(_async_start_attached_container(endpoint))


async def _async_start_attached_container(endpoint):
    async with websockets.connect(endpoint) as websocket:
        hello_msg = await websocket.recv()
        if hello_msg == "OK":
            await listen_for_messages(websocket)
        elif hello_msg[:6] == "ERROR:":
            click.echo(hello_msg[6:])
            await listen_for_messages(websocket)
        else:
            click.echo("error starting container #{container_id}")


def _start_interactive_container(container_id, tty):
    exec_id = _create_exec_instance(container_id, tty)
    endpoint = _build_endpoint(exec_id)
    if exec_id is not None:
        asyncio.run(_async_start_interactive_container(endpoint))


async def _async_start_interactive_container(endpoint):
    loop = asyncio.get_running_loop()
    async with websockets.connect(endpoint) as websocket:
        for signame in ["SIGINT", "SIGTERM"]:
            loop.add_signal_handler(
                getattr(signal, signame),
                functools.partial(close_websocket, websocket, loop),
            )

        hello_msg = await websocket.recv()
        if hello_msg == "OK":
            loop = asyncio.get_event_loop()
            loop.add_reader(sys.stdin, send_user_input, websocket)
            await listen_for_messages(websocket)
        elif hello_msg[:6] == "ERROR:":
            click.echo(hello_msg[6:])
            await listen_for_messages(websocket)
        else:
            click.echo("error starting container #{container_id}")


def _build_endpoint(exec_id):
    return WS_EXEC_START_URL.format(
        exec_id=exec_id,
        options=urllib.parse.urlencode({"attach": "true", "start_container": "true"}),
    )


def send_user_input(websocket):
    tasks = []
    input_line = sys.stdin.readline()
    task = asyncio.ensure_future(websocket.send(input_line))
    tasks.append(task)


def start_container(container_id, tty=False):
    exec_id = _create_exec_instance(container_id, tty)
    if exec_id is not None:
        asyncio.run(_start_container(container_id, exec_id, tty))


async def _start_container(container_id, exec_id, tty):
    endpoint = WS_EXEC_START_URL.format(
        exec_id=exec_id,
        options=urllib.parse.urlencode({"attach": "false", "start_container": "true"}),
    )

    async with websockets.connect(endpoint) as websocket:
        await websocket.wait_closed()
        if websocket.close_code != 1001:
            click.echo("error starting container #{container_id}")


def close_websocket(websocket, loop):
    task = asyncio.create_task(_close_websocket(websocket))
    asyncio.ensure_future(task)


async def _close_websocket(websocket):
    await websocket.close(code=1000, reason="interrupted by user")


def _create_exec_instance(container_id, tty):
    exec_config = ExecConfig.from_dict(
        {"container_id": container_id, "cmd": [], "env": [], "user": "", "tty": tty}
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
    if response.status_code == 201:
        click.echo(f"created execution instance {response.parsed.id}")
        return response.parsed.id

    click.echo(f"{container_id}: error creating execution instance: {response.parsed}")
    return None


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
                500: "kleened backend error",
            },
        )
        if response is None or response.status_code != 200:
            break
