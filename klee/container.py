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
from .network import connect_
from .printing import (
    echo_bold,
    echo_error,
    command_cls,
    group_cls,
    print_websocket_closing,
    print_table,
    unexpected_error,
)
from .connection import create_websocket
from .utils import human_duration, request_and_validate_response, listen_for_messages
from .prune import prune_command
from .inspect import inspect_command

HELP_DETACH_FLAG = """
Do not output STDOUT/STDERR to the terminal.
If this is set, Klee will exit and return the container ID when the container has been started.
"""
HELP_INTERACTIVE_FLAG = (
    "Send terminal input to container's STDIN. If set, `--detach` will be ignored."
)

HELP_NETWORK_DRIVER_FLAG = """
Network driver of the container.
Possible values are `ipnet`, `host`, `vnet`, and `disabled`.
"""

HELP_IP_FLAG = "IPv4 address used for the container. If omitted, an unused ip is allocated from the IPv4 subnet of `--network`."

HELP_IP6_FLAG = "IPv6 address used for the container. If omitted, an unused ip is allocated from the IPv6 subnet of `--network`."

WS_EXEC_START_ENDPOINT = "/exec/start"

EXEC_INSTANCE_CREATED = "created execution instance {exec_id}"
EXEC_INSTANCE_CREATE_ERROR = (
    "{container_id}: error creating execution instance: {exec_id}"
)
EXEC_START_ERROR = "error starting container"


START_ONLY_ONE_CONTAINER_WHEN_ATTACHED = (
    "only one container can be started when attaching to container I/O."
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
@click.group(cls=group_cls())
def root(name="container"):
    """Manage containers"""


def container_create(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        context_settings={"ignore_unknown_options": True},
    )
    @click.option("--name", default="", help="Assign a name to the container")
    @click.option(
        "--user",
        "-u",
        metavar="text",
        default="",
        help="Alternate user that should be used for starting the container",
    )
    @click.option(
        "--env",
        "-e",
        multiple=True,
        default=None,
        help="Set environment variables (e.g. --env FIRST=SomeValue --env SECOND=AnotherValue)",
    )
    @click.option(
        "--mount",
        "-m",
        multiple=True,
        default=None,
        metavar="list",
        help="""
        Mount a volume/directory/file on the host filesystem into the container.
        Mounts are specfied using a `--mount <source>:<destination>[:rw|ro]` syntax.
        """,
    )
    @click.option(
        "--jailparam",
        "-J",
        multiple=True,
        default=["mount.devfs", 'exec.stop="/bin/sh /etc/rc.shutdown jail"'],
        show_default=True,
        help="Specify a jail parameters, see jail(8) for details",
    )
    @click.option("--driver", "-l", default=None, help=HELP_NETWORK_DRIVER_FLAG)
    @click.option(
        "--network", "-n", default=None, help="Connect container to this network."
    )
    @click.option("--ip", default=None, help=HELP_IP_FLAG)
    @click.option("--ip6", default=None, help=HELP_IP6_FLAG)
    @click.argument("image", nargs=1)
    @click.argument("command", nargs=-1)
    def create(**kwargs):
        """
        Create a new container. The **IMAGE** parameter syntax is:
        `<image_id>|[<image_name>[:<tag>]][@<snapshot_id>]`

        See the documentation for details.
        """
        create_container_and_connect_to_network(**kwargs)

    return create


root.add_command(container_create("create"), name="create")


def create_container_and_connect_to_network(**kwargs):
    kwargs_create = {
        "name": kwargs["name"],
        "image": kwargs["image"],
        "command": kwargs["command"],
        "user": kwargs["user"],
        "mount": kwargs["mount"],
        "env": kwargs["env"],
        "jailparam": kwargs["jailparam"],
        "network_driver": kwargs["driver"],
    }
    response = create_(**kwargs_create)

    if response is None or response.status_code != 201:
        echo_error("could not create container: ", response.parsed.message)
        return

    container_id = response.parsed.id

    if kwargs["network"] is None:
        return container_id

    kwargs_connect = {
        "ip": kwargs["ip"],
        "ip6": kwargs["ip6"],
        "network": kwargs["network"],
        "container": container_id,
    }
    response = connect_(**kwargs_connect)
    if response is None or response.status_code != 204:
        echo_error(f"could not connect container: {response.parsed.message}")
        return

    return container_id


def create_(**kwargs):
    mounts = [] if kwargs["mount"] is None else list(kwargs["mount"])

    container_config = {
        "name": kwargs["name"],
        "image": kwargs["image"],
        "cmd": list(kwargs["command"]),
        "user": kwargs["user"],
        "env": list(kwargs["env"]),
        "mounts": [decode_mount(mnt) for mnt in mounts],
        "jail_param": list(kwargs["jailparam"]),
        "network_driver": kwargs["network_driver"],
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


def decode_mount(mount):
    sections = mount.split(":")
    if len(sections) > 3:
        echo_error(f"invalid mount format '{mount}'. Max 3 elements seperated by ':'.")
        sys.exit(125)

    if len(sections) < 2:
        echo_error(
            f"invalid mount format '{mount}'. Must have at least 2 elements seperated by ':'."
        )
        sys.exit(125)

    if len(sections) == 3 and sections[-1] not in {"ro", "rw"}:
        echo_error(
            f"invalid mount format '{mount}'. Last element should be either 'ro' or 'rw'."
        )
        sys.exit(125)

    if len(sections) == 3:
        source, destination, mode = sections
        read_only = True if mode == "ro" else False
    else:
        source, destination = sections
        read_only = False

    if source[:1] == "/":
        mount_type = "nullfs"
    else:
        mount_type = "volume"

    return {
        "type": mount_type,
        "source": source,
        "destination": destination,
        "read_only": read_only,
    }


def container_list(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
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
                200: lambda response: _print_container(response),
                500: "kleened backend error",
            },
        )

    return listing


root.add_command(container_list("ls"), name="ls")


def _print_container(response):
    containers = response.parsed

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
            command_json2command_human(c.cmd),
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
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.option(
        "--force",
        "-f",
        is_flag=True,
        default=False,
        help="Stop containers before removing them.",
    )
    @click.argument("containers", required=True, nargs=-1)
    def remove(force, containers):
        """Remove one or more containers"""
        for container_id in containers:
            if force:
                _stop([container_id], silent=True)

            response = request_and_validate_response(
                container_remove_endpoint,
                kwargs={"container_id": container_id},
                statuscode2messsage={
                    200: lambda response: response.parsed.id,
                    404: lambda response: response.parsed.message,
                    409: lambda response: response.parsed.message,
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
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.option("--detach", "-d", default=False, is_flag=True, help=HELP_DETACH_FLAG)
    @click.option(
        "--interactive", "-i", default=False, is_flag=True, help=HELP_INTERACTIVE_FLAG
    )
    @click.option(
        "--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY"
    )
    @click.argument("containers", required=True, nargs=-1)
    def start(detach, interactive, tty, containers):
        """Start one or more stopped containers.
        Attach only if a single container is started
        """
        start_(detach, interactive, tty, containers)

    return start


root.add_command(container_start("start"), name="start")


def container_stop(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("containers", nargs=-1)
    def stop(containers):
        """Stop one or more running containers"""
        _stop(containers)

    return stop


def _stop(containers, silent=False):
    def ssch(_):
        return ""

    def return_id(response):
        return response.parsed.id

    if silent:
        response_200 = ssch
    else:
        response_200 = return_id

    for container_id in containers:
        response = request_and_validate_response(
            container_stop_endpoint,
            kwargs={"container_id": container_id},
            statuscode2messsage={
                200: response_200,
                304: lambda response: response.parsed.message,
                404: lambda response: response.parsed.message,
                500: "kleened backend error",
            },
        )
        if response is None or response.status_code != 200:
            break


root.add_command(container_stop("stop"), name="stop")


def container_restart(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
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
                detach=True,
                start_container="true",
            )

    return restart


root.add_command(container_restart("restart"), name="restart")


def container_exec(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name="exec",
        hidden=hidden,
        no_args_is_help=True,
        # We use this to avoid problems option-parts of the "command" argument, i.e., 'klee container exec -a /bin/sh -c echo lol
        context_settings={"ignore_unknown_options": True},
    )
    @click.option("--detach", "-d", default=False, is_flag=True, help=HELP_DETACH_FLAG)
    @click.option(
        "--env",
        "-e",
        multiple=True,
        default=None,
        help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)",
    )
    @click.option(
        "--interactive", "-i", default=False, is_flag=True, help=HELP_INTERACTIVE_FLAG
    )
    @click.option(
        "--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY"
    )
    @click.option(
        "--user", "-u", default="", help="Username or UID of the executing user"
    )
    @click.argument("container", nargs=1)
    @click.argument("command", nargs=-1)
    def exec_(detach, env, interactive, tty, user, container, command):
        """
        Run a command in a container
        """
        start_container = "true"
        execution_create_and_start(
            container, tty, interactive, detach, start_container, command, env, user
        )

    return exec_


root.add_command(container_exec("exec"), name="exec")


def container_update(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        # context_settings={"ignore_unknown_options": True},
    )
    @click.option("--name", default=None, help="Assign a new name to the container")
    @click.option(
        "--user",
        "-u",
        metavar="text",
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
        help="Specify one or more jail parameters, see jail(8) for details",
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
            "jail_param": jailparam,
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
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
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
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        # 'ignore_unknown_options' because the user can supply an arbitrary command
        context_settings={"ignore_unknown_options": True},
    )
    @click.option("--name", default="", help="Assign a name to the container")
    @click.option(
        "--user",
        "-u",
        default="",
        help="""
        Alternate user that should be used for starting the container.
        This parameter will be overwritten by the jail parameter `exec.jail_user` if it is set.
        """,
    )
    @click.option(
        "--mount",
        "-m",
        multiple=True,
        default=None,
        metavar="list",
        help="""
        Mount a volume/directory/file on the host filesystem into the container.
        Mounts are specfied using a `--mount <source>:<destination>[:rw|ro]` syntax.
        """,
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
        help="""
        Specify one or more jail parameters to use. See the `jail(8)` man-page for details.
        If you do not want `exec.clean` and `mount.devfs` enabled, you must actively disable them.
        """,
    )
    @click.option("--driver", "-l", default="ipnet", help=HELP_NETWORK_DRIVER_FLAG)
    @click.option(
        "--network", "-n", default=None, help="Connect a container to a network"
    )
    @click.option("--ip", default=None, help=HELP_IP_FLAG)
    @click.option("--ip6", default=None, help=HELP_IP6_FLAG)
    @click.option(
        "--detach",
        "-d",
        default=False,
        is_flag=True,
        metavar="flag",
        help=HELP_DETACH_FLAG,
    )
    @click.option(
        "--interactive", "-i", default=False, is_flag=True, help=HELP_INTERACTIVE_FLAG
    )
    @click.option(
        "--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY"
    )
    @click.argument("image", nargs=1)
    @click.argument("command", nargs=-1)
    def run(**kwargs):
        """
        Run a command in a new container.

        The IMAGE syntax is: (**IMAGE_ID**|**IMAGE_NAME**[:**TAG**])[:**@SNAPSHOT**]
        """
        kwargs_start = {
            "detach": kwargs.pop("detach"),
            "interactive": kwargs.pop("interactive"),
            "tty": kwargs.pop("tty"),
        }

        container_id = create_container_and_connect_to_network(**kwargs)
        if container_id is None:
            return

        kwargs_start["containers"] = [container_id]
        start_(**kwargs_start)

    return run


root.add_command(container_run("run"), name="run")


def start_(detach, interactive, tty, containers):
    if interactive:
        detach = False

    if not detach and len(containers) != 1:
        echo_bold(START_ONLY_ONE_CONTAINER_WHEN_ATTACHED)
    else:
        for container in containers:
            start_container = True
            execution_create_and_start(
                container, tty, interactive, detach, start_container
            )


def execution_create_and_start(
    container_id, tty, interactive, detach, start_container, cmd=None, env=None, user=""
):
    cmd = [] if cmd is None else cmd
    env = [] if env is None else env
    attach = not detach
    exec_id = _create_exec_instance(container_id, tty, cmd, env, user)
    if exec_id is not None:
        exec_config = json.dumps(
            {"exec_id": exec_id, "attach": attach, "start_container": start_container}
        )

        if attach:
            asyncio.run(_attached_execute(exec_config, interactive))
        else:
            asyncio.run(_execute(exec_config))


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
        echo_bold(EXEC_INSTANCE_CREATED.format(exec_id=response.parsed.id))
        return response.parsed.id

    echo_bold(
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
            echo_bold(EXEC_START_ERROR)


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
                print_websocket_closing(closing_message, ["message"])

            else:
                print_websocket_closing(closing_message, ["message", "data"])

        elif start_msg["msg_type"] == "error":
            print_websocket_closing(closing_message, ["message"])

        else:
            unexpected_error()


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
