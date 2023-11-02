import signal
import asyncio
import sys
import functools

import json

import click

from .client.api.default.container_create import (
    sync_detailed as container_create_endpoint,
)
from .client.api.default.container_list import sync_detailed as container_list_endpoint
from .client.api.default.container_remove import (
    sync_detailed as container_remove_endpoint,
)
from .client.api.default.container_prune import (
    sync_detailed as container_prune_endpoint,
)
from .client.api.default.container_stop import sync_detailed as container_stop_endpoint
from .client.api.default.exec_create import sync_detailed as exec_create_endpoint
from .client.api.default.container_inspect import (
    sync_detailed as container_inspect_endpoint,
)
from .client.api.default.container_update import (
    sync_detailed as container_update_endpoint,
)

from .client.models.container_config import ContainerConfig
from .client.models.exec_config import ExecConfig
from .name_generator import random_name
from .network import connect_
from .richclick import console, print_table
from .connection import create_websocket
from .utils import (
    KLEE_MSG,
    UNEXPECTED_ERROR,
    human_duration,
    request_and_validate_response,
    listen_for_messages,
    print_closing,
)
from .prune import prune_command
from .inspect import inspect_command
from .config import config


WS_EXEC_START_ENDPOINT = "/exec/start"

EXEC_INSTANCE_CREATED = KLEE_MSG.format(msg="created execution instance {exec_id}")
EXEC_INSTANCE_CREATE_ERROR = KLEE_MSG.format(
    msg="{container_id}: error creating execution instance: {exec_id}"
)
EXEC_START_ERROR = KLEE_MSG.format(msg="error starting container")


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
@click.group(cls=config.group_cls)
def root(name="container"):
    """Manage containers"""


def container_create(name, hidden=False):
    @click.command(
        cls=config.command_cls,
        name=name,
        hidden=hidden,
        context_settings={"ignore_unknown_options": True},
    )
    @click.option("--name", default="", help="Assign a name to the container")
    @click.option(
        "--user",
        "-u",
        metavar="TEXT",
        default="",
        help="Alternate user that should be used for starting the container",
    )
    @click.option(
        "--network", "-n", default=None, help="Connect a container to a network."
    )
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

    return create


root.add_command(container_create("create"), name="create")


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

    if name == "":
        name = random_name()

    container_config = {
        "name": name,
        "cmd": list(command),
        "volumes": volumes,
        "image": image,
        "jail_param": list(jailparam),
        "env": list(env),
        "user": user,
    }
    container_config = ContainerConfig.from_dict(container_config)

    return request_and_validate_response(
        container_create_endpoint,
        kwargs={"json_body": container_config},
        statuscode2messsage={
            201: lambda response: response.parsed.id,
            404: lambda response: response.parsed.message,
            500: lambda response: response.parsed,
        },
    )


def container_list(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    @click.option(
        "--all",
        "-a",
        default=False,
        is_flag=True,
        help="Show all containers (default shows only running containers)",
    )
    def listing(**kwargs):
        """List containers"""
        request_and_validate_response(
            container_list_endpoint,
            kwargs={"all_": kwargs["all"]},
            statuscode2messsage={
                200: lambda response: _print_container(response.parsed),
                500: "kleened backend error",
            },
        )

    return listing


root.add_command(container_list("ls"), name="ls")


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


root.add_command(
    inspect_command(
        name="inspect",
        argument="container",
        id_var="container_id",
        docs="Display detailed information on a container.",
        endpoint=container_inspect_endpoint,
    ),
    name="inspect",
)


def container_remove(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    @click.argument("containers", required=True, nargs=-1)
    def remove(containers):
        """Remove one or more containers"""
        for container_id in containers:
            response = request_and_validate_response(
                container_remove_endpoint,
                kwargs={"container_id": container_id},
                statuscode2messsage={
                    200: lambda response: response.parsed.id,
                    404: lambda response: response.parsed.message,
                    500: "kleened backend error",
                },
            )
            if response is None or response.status_code != 200:
                break

    return remove


root.add_command(container_remove("rm"), name="rm")


root.add_command(
    prune_command(
        name="prune",
        docs="Remove all stopped containers.",
        warning="WARNING! This will remove all stopped containers.",
        endpoint=container_prune_endpoint,
    )
)


def container_start(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
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
    @click.option(
        "--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY"
    )
    @click.argument("containers", required=True, nargs=-1)
    def start(attach, interactive, tty, containers):
        """Start one or more stopped containers.
        Attach only if a single container is started
        """
        start_(attach, interactive, tty, containers)

    return start


root.add_command(container_start("start"), name="start")


def container_stop(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    @click.argument("containers", nargs=-1)
    def stop(containers):
        """Stop one or more running containers"""
        for container_id in containers:
            response = request_and_validate_response(
                container_stop_endpoint,
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

    return stop


root.add_command(container_stop("stop"), name="stop")


def container_restart(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    @click.argument("containers", nargs=-1)
    def restart(containers):
        """Restart one or more containers"""
        for container_id in containers:
            response = request_and_validate_response(
                container_stop_endpoint,
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

            execution_create_and_start(
                response.parsed.id,
                tty=False,
                interactive=False,
                attach=False,
                start_container="true",
            )

    return restart


root.add_command(container_restart("restart"), name="restart")


def start_(attach, interactive, tty, containers):
    if attach and len(containers) != 1:
        console.print(START_ONLY_ONE_CONTAINER_WHEN_ATTACHED)
    else:
        for container in containers:
            start_container = True
            execution_create_and_start(
                container, tty, interactive, attach, start_container
            )


def container_exec(name, hidden=False):
    @click.command(cls=config.command_cls, name="exec", hidden=hidden)
    @click.option(
        "--attach", "-a", default=False, is_flag=True, help="Attach to STDOUT/STDERR"
    )
    @click.option(
        "--env",
        "-e",
        multiple=True,
        default=None,
        help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)",
    )
    @click.option(
        "--interactive",
        "-i",
        default=False,
        is_flag=True,
        help="Send terminal input to STDIN. Ignored if '--attach' is not used.",
    )
    @click.option(
        "--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY"
    )
    @click.option(
        "--user", "-u", default="", help="Username or UID of the executing user"
    )
    @click.argument("container", nargs=1)
    @click.argument("command", nargs=-1)
    def exec_(attach, env, interactive, tty, user, container, command):
        """
        Run a command in a container
        """
        start_container = "true"
        execution_create_and_start(
            container, tty, interactive, attach, start_container, command, env, user
        )

    return exec_


root.add_command(container_exec("exec"), name="exec")


def container_update(name, hidden=False):
    @click.command(
        cls=config.command_cls,
        name=name,
        hidden=hidden,
        # context_settings={"ignore_unknown_options": True},
    )
    @click.option("--name", default=None, help="Assign a new name to the container")
    @click.option(
        "--user",
        "-u",
        metavar="TEXT",
        default=None,
        help="Alternate user that should be used for starting the container",
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
        default=None,
        show_default=True,
        help="Specify a jail parameters, see jail(8) for details",
    )
    @click.argument("container", nargs=1)
    @click.argument("command", nargs=-1)
    def update(name, user, env, jailparam, container, command):
        """
        See the documentation for details.
        """
        config = {
            "name": name,
            "user": user,
            "env": env,
            "jailparam": jailparam,
            "container": container,
        }

        config["cmd"] = None if len(command) == 0 else list(command)
        config = ContainerConfig.from_dict(config)
        request_and_validate_response(
            container_update_endpoint,
            kwargs={"container_id": container, "json_body": config},
            statuscode2messsage={
                201: lambda response: response.parsed.id,
                409: lambda response: response.parsed.message,
                404: lambda response: response.parsed.message,
            },
        )

    return update


root.add_command(container_update("update"), name="update")


def container_rename(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    @click.argument("container", nargs=1)
    @click.argument("name", nargs=1)
    def rename(container, name):
        """
        Rename a container.
        """
        config = ContainerConfig.from_dict({"name": name})
        request_and_validate_response(
            container_update_endpoint,
            kwargs={"container_id": container, "json_body": config},
            statuscode2messsage={
                201: lambda response: response.parsed.id,
                409: lambda response: response.parsed.message,
                404: lambda response: response.parsed.message,
            },
        )

    return rename


root.add_command(container_rename("rename"), name="rename")


def container_run(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    # what is this used for? context_settings={"ignore_unknown_options": True},
    @click.option("--name", default="", help="Assign a name to the container")
    @click.option(
        "--user",
        "-u",
        default="",
        help="Alternate user that should be used for starting the container",
    )
    @click.option(
        "--network", "-n", default=None, help="Connect a container to a network"
    )
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
        default=["mount.devfs"],
        show_default=True,
        help="Specify a jail parameters, see jail(8) for details",
    )
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
    @click.option(
        "--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY"
    )
    @click.argument("image", nargs=1)
    @click.argument("command", nargs=-1)
    def run(
        name,
        user,
        network,
        ip,
        volume,
        env,
        jailparam,
        attach,
        interactive,
        tty,
        image,
        command,
    ):
        """
        Create and start a command in a new container.

        The IMAGE parameter syntax is: (**IMAGE_ID**|**IMAGE_NAME**[:**TAG**])[:**@SNAPSHOT**]
        """
        response = create_(
            name, user, network, ip, volume, env, jailparam, image, command
        )
        if response is None or response.status_code != 201:
            return

        container_id = response.parsed.id
        if network is not None:
            response = connect_(ip, network, container_id)
            if response is None or response.status_code != 204:
                console.print(KLEE_MSG.format(msg="could not start container"))
                return

        start_(attach, interactive, tty, [container_id])

    return run


root.add_command(container_run("run"), name="run")


def execution_create_and_start(
    container_id, tty, interactive, attach, start_container, cmd=None, env=None, user=""
):
    cmd = [] if cmd is None else cmd
    env = [] if env is None else env
    exec_id = _create_exec_instance(container_id, tty, cmd, env, user)
    if exec_id is not None:
        config = json.dumps(
            {"exec_id": exec_id, "attach": attach, "start_container": start_container}
        )

        if attach:
            asyncio.run(_attached_execute(config, interactive))
        else:
            asyncio.run(_execute(config))


def _create_exec_instance(container_id, tty, cmd, env, user):
    exec_config = ExecConfig.from_dict(
        {"container_id": container_id, "cmd": cmd, "env": env, "user": user, "tty": tty}
    )
    response = request_and_validate_response(
        exec_create_endpoint,
        kwargs={"json_body": exec_config},
        statuscode2messsage={
            201: lambda response: "",
            404: lambda response: response.parsed.message,
            500: lambda response: response.parsed,
        },
    )
    if response.status_code == 201:
        console.print(EXEC_INSTANCE_CREATED.format(exec_id=response.parsed.id))
        return response.parsed.id

    console.print(
        EXEC_INSTANCE_CREATE_ERROR.format(
            container_id=container_id, exec_id=response.parsed
        )
    )
    return None


async def _execute(config):
    async with create_websocket(WS_EXEC_START_ENDPOINT) as websocket:
        await websocket.send(config)
        await websocket.wait_closed()
        if websocket.close_code != 1001:
            console.print(EXEC_START_ERROR)


async def _attached_execute(config, interactive):
    loop = asyncio.get_running_loop()
    async with create_websocket(WS_EXEC_START_ENDPOINT) as websocket:
        if interactive:
            for signame in ["SIGINT", "SIGTERM"]:
                loop.add_signal_handler(
                    getattr(signal, signame),
                    functools.partial(_close_websocket, websocket),
                )

        await websocket.send(config)
        starting_frame = await websocket.recv()
        start_msg = json.loads(starting_frame)

        if start_msg["msg_type"] == "starting":
            if interactive:
                loop = asyncio.get_event_loop()
                loop.add_reader(sys.stdin, _send_user_input, websocket)
            closing_message = await listen_for_messages(websocket)
            if closing_message["data"] == "":
                print_closing(closing_message, ["message"])

            else:
                print_closing(closing_message, ["message", "data"])

        elif start_msg["msg_type"] == "error":
            print_closing(closing_message, ["message"])

        else:
            console.print(UNEXPECTED_ERROR)


def _send_user_input(websocket):
    tasks = []
    input_line = sys.stdin.readline()
    task = asyncio.ensure_future(websocket.send(input_line))
    tasks.append(task)


def _close_websocket(websocket):
    async def _close_ws(websocket):
        await websocket.close(code=1000, reason="interrupted by user")

    task = asyncio.create_task(_close_ws(websocket))
    asyncio.ensure_future(task)
