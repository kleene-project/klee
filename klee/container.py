import json

import click

from .client.api.default.container_create import sync_detailed as container_create
from .client.api.default.container_list import sync_detailed as container_list
from .client.api.default.container_remove import sync_detailed as container_remove
from .client.api.default.container_stop import sync_detailed as container_stop
from .client.models.container_config import ContainerConfig
from .name_generator import random_name
from .network import connect_
from .exec import execution_create_and_start
from .richclick import console, print_table, RichCommand, RichGroup
from .utils import KLEE_MSG, human_duration, request_and_validate_response

START_ONLY_ONE_CONTAINER_WHEN_ATTACHED = KLEE_MSG.format(
    msg="only one container can be started when setting the 'attach' flag."
)

CONTAINER_LIST_COLUMNS = [
    ("CONTAINER ID", {"style": "cyan", "min_width": 13}),
    ("NAME", {"style": "bold aquamarine1"}),
    ("IMAGE", {"style": "bold bright_magenta"}),
    ("TAG", {"style": "aquamarine1"}),
    ("COMMAND", {"style": "bright_white"}),
    ("CREATED", {"style": "bright_white"}),
    ("STATUS", {}),
]


# pylint: disable=unused-argument
@click.group(cls=RichGroup)
def root(name="container"):
    """Manage containers"""


@root.command(
    cls=RichCommand, name="create", context_settings={"ignore_unknown_options": True}
)
@click.option("--name", default="", help="Assign a name to the container")
@click.option(
    "--user",
    "-u",
    metavar="TEXT",
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
    """
    Create a new container. The **IMAGE** parameter syntax is:
    `<image_id>|[<image_name>[:<tag>]][:@<snapshot_id>]`

    See the documentation for details.
    """
    create_container_and_connect_to_network(
        name, user, network, ip, volume, env, jailparam, image, command
    )


def create_container_and_connect_to_network(
    name, user, network, ip, volume, env, jailparam, image, command
):
    response = create_(name, user, network, ip, volume, env, jailparam, image, command)

    if response is None or response.status_code != 201:
        return

    if network is None:
        return

    return connect_(ip, network, response.parsed.id)


def create_(name, user, network, ip, volume, env, jailparam, image, command):
    if volume is None:
        volumes = []
    else:
        volumes = list(volume)

    container_config = {
        "cmd": list(command),
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


@root.command(cls=RichCommand, name="ls")
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
    def command_json2command_human(command_str):
        return " ".join(json.loads(command_str))

    def is_running_str(running):
        if running:
            return "[green]running[/green]"
        return "[red]stopped[/red]"

    containers = [
        [
            c.id,
            c.name,
            c.image_id,
            c.image_tag,
            command_json2command_human(c.command),
            human_duration(c.created) + " ago",
            is_running_str(c.running),
        ]
        for c in containers
    ]
    print_table(containers, CONTAINER_LIST_COLUMNS)


@root.command(cls=RichCommand, name="rm")
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


@root.command(cls=RichCommand, name="start")
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
    if attach and len(containers) != 1:
        console.print(START_ONLY_ONE_CONTAINER_WHEN_ATTACHED)
    else:
        for container in containers:
            start_container = True
            execution_create_and_start(
                container, tty, interactive, attach, start_container
            )


@root.command(cls=RichCommand, name="stop")
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
