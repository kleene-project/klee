import signal
import asyncio
import sys
import functools
import tty
import termios
import json

import websockets
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
from .network import _connect
from .printing import (
    echo_bold,
    echo_error,
    command_cls,
    group_cls,
    print_response_id,
    print_response_msg,
    print_backend_error,
    print_nothing,
    print_websocket_closing,
    print_image_column,
    is_running_str,
    print_table,
    unexpected_error,
)
from .name_generator import random_name
from .connection import create_websocket
from .utils import (
    human_duration,
    request_and_print_response,
    listen_for_messages,
    decode_mount,
    decode_public_ports,
)
from .prune import prune_command
from .inspect import inspect_command
from .options import container_create_options, exec_options

HELP_PUBLISH_FLAG = """
Publish ports using the syntax **HOST_PORT[:CONTAINER_PORT][/PROTOCOL]** or
**INTERFACE:HOST_PORT:CONTAINER_PORT[/PROTOCOL]**.
**CONTAINER_PORT** defaults to **HOST_PORT** and **PROTOCOL** defaults to 'tcp'.
"""


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
    ("IMAGE", {"style": "blue"}),
    ("COMMAND", {"style": "bright_white", "max_width": 40, "no_wrap": True}),
    ("CREATED", {"style": "bright_white"}),
    ("AUTORUN", {"style": "bright_white", "justify": "center"}),
    ("STATUS", {}),
    ("JID", {"style": "white"}),
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
        context_settings={"ignore_unknown_options": True},
        no_args_is_help=True,
    )
    def create(**kwargs):
        """
        Create a new container. The **IMAGE** parameter syntax is:
        **IMAGE_ID|[IMAGE_NAME[:TAG]][@SNAPSHOT_ID]**

        See the documentation for details.
        """
        _create_container_and_connect_to_network(**kwargs)

    create.params.extend(container_create_options())
    opts_args = [
        click.Option(["--publish", "-p"], multiple=True, help=HELP_PUBLISH_FLAG),
        click.Option(["--name"], default=None, help="Assign a name to the container"),
        click.Argument(["image"], nargs=1),
        click.Argument(["command"], nargs=-1),
    ]
    create.params.extend(opts_args)
    return create


def container_list(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
    @click.option(
        "--all",
        "-a",
        default=False,
        is_flag=True,
        help="Show all containers (default only shows running containers)",
    )
    def listing(**kwargs):
        """List containers"""
        request_and_print_response(
            container_list_endpoint,
            kwargs={"all_": kwargs["all"]},
            statuscode2printer={200: _print_container, 500: print_backend_error},
        )

    return listing


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

            response = request_and_print_response(
                container_remove_endpoint,
                kwargs={"container_id": container_id},
                statuscode2printer={
                    200: print_response_id,
                    404: print_response_msg,
                    409: print_response_msg,
                    500: print_backend_error,
                },
            )
            if response is None or response.status_code != 200:
                break

    return remove


def container_start(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    def start(detach, interactive, tty, containers):
        """Start one or more stopped containers.
        Attach only if a single container is started
        """
        _start(detach, interactive, tty, containers)

    start = exec_options(start)
    start.params.append(click.Argument(["containers"], required=True, nargs=-1))
    return start


def container_stop(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("containers", nargs=-1)
    def stop(containers):
        """Stop one or more running containers"""
        _stop(containers)

    return stop


def container_restart(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("containers", nargs=-1)
    def restart(containers):
        """Restart one or more containers"""
        for container_id in containers:
            response = request_and_print_response(
                container_stop_endpoint,
                kwargs={"container_id": container_id},
                statuscode2printer={
                    200: print_response_id,
                    304: print_response_msg,
                    404: print_response_msg,
                    500: print_backend_error,
                },
            )
            if response is None or response.status_code != 200:
                break

            _execution_create_and_start(
                response.parsed.id,
                tty=False,
                interactive=False,
                detach=True,
                start_container="true",
            )

    return restart


def container_exec(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name="exec",
        hidden=hidden,
        no_args_is_help=True,
        # We use this to avoid problems option-parts of the "command" argument, i.e., 'klee container exec -a /bin/sh -c echo lol
        context_settings={"ignore_unknown_options": True},
    )
    def exec_(detach, interactive, tty, env, user, container, command):
        """
        Run a command in a container
        """
        start_container = "true"
        _execution_create_and_start(
            container, tty, interactive, detach, start_container, command, env, user
        )

    exec_ = exec_options(exec_)
    exec_.params.extend(
        [
            click.Option(
                ["--env", "-e"],
                multiple=True,
                default=None,
                metavar="list",
                help="Set environment variables (e.g. `--env FIRST=value1 --env SECOND=value2`)",
            ),
            click.Option(
                ["--user", "-u"],
                default="",
                help="Username or UID of the user running the process",
            ),
            click.Argument(["container"], nargs=1),
            click.Argument(["command"], nargs=-1),
        ]
    )

    return exec_


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
        default=None,
        help="Default user used when running commands in the container",
    )
    @click.option(
        "--env",
        "-e",
        multiple=True,
        default=None,
        metavar="list",
        help="Set environment variables (e.g. `--env FIRST=env --env SECOND=env`)",
    )
    @click.option(
        "--jailparam",
        "-J",
        multiple=True,
        default=None,
        metavar="list",
        help="""
        Set jail parameters. Replace defaults (such as 'mount.devfs', 'exec.clean', etc.) by specifying alternative values. See docs for details.
        """,
    )
    @click.option(
        "--persist",
        "-P",
        is_flag=True,
        metavar="flag",
        help="Do not remove this container when pruning",
    )
    @click.option(
        "--restart",
        default="no",
        show_default=True,
        help="""
        Restarting policy of the container. Set to 'no' for no automatic restart of the container.
        Set to 'on-startup' to start the container each time Kleened is.
        """,
    )
    @click.argument("container", nargs=1)
    @click.argument("command", nargs=-1)
    def update(**config):
        """
        Modify container properties.
        Using `jailparam` and `env` removes all values from the existing configration.
        """
        container_id = config["container"]

        config["jail_param"] = config.pop("jailparam")
        config["restart_policy"] = config.pop("restart")
        command = config.pop("command")
        config["cmd"] = None if len(command) == 0 else list(command)

        config = ContainerConfig.from_dict(config)

        request_and_print_response(
            container_update_endpoint,
            kwargs={"container_id": container_id, "json_body": config},
            statuscode2printer={
                201: print_response_id,
                409: print_response_msg,
                404: print_response_msg,
            },
        )

    return update


def container_rename(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("container", nargs=1)
    @click.argument("new_name", nargs=1)
    def rename(container, new_name):
        """
        Rename a container.
        """
        config = ContainerConfig.from_dict({"name": new_name})
        request_and_print_response(
            container_update_endpoint,
            kwargs={"container_id": container, "json_body": config},
            statuscode2printer={
                201: print_response_id,
                409: print_response_msg,
                404: print_response_msg,
            },
        )

    return rename


def container_run(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        # 'ignore_unknown_options' because the user can supply an arbitrary command
        context_settings={"ignore_unknown_options": True},
    )
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

        container_id = _create_container_and_connect_to_network(**kwargs)
        if container_id is None:
            return

        kwargs_start["containers"] = [container_id]
        _start(**kwargs_start)

    run.params.extend(container_create_options())
    run = exec_options(run)
    opts_args = [
        click.Option(["--name"], default=None, help="Assign a name to the container"),
        click.Option(["--publish", "-p"], multiple=True, help=HELP_PUBLISH_FLAG),
        click.Argument(["image"], nargs=1),
        click.Argument(["command"], nargs=-1),
    ]
    run.params.extend(opts_args)
    return run


def container_inspect(name, hidden=False):
    return inspect_command(
        name=name,
        hidden=hidden,
        argument="container",
        id_var="container_id",
        docs="Display detailed information on a container.",
        endpoint=container_inspect_endpoint,
    )


root.add_command(container_create("create"), name="create")
root.add_command(container_list("ls"), name="ls")
root.add_command(container_inspect("inspect"), name="inspect")
root.add_command(container_remove("rm"), name="rm")
root.add_command(
    prune_command(
        name="prune",
        docs="Remove all stopped containers.",
        warning="WARNING! This will remove all stopped containers.",
        endpoint=container_prune_endpoint,
    )
)
root.add_command(container_start("start"), name="start")
root.add_command(container_stop("stop"), name="stop")
root.add_command(container_restart("restart"), name="restart")
root.add_command(container_exec("exec"), name="exec")
root.add_command(container_update("update"), name="update")
root.add_command(container_rename("rename"), name="rename")
root.add_command(container_run("run"), name="run")


def _create_container_and_connect_to_network(**kwargs):
    if kwargs["network"] is None and kwargs["driver"] is None:
        kwargs["driver"] = "host"

    if kwargs["network"] is not None and kwargs["driver"] is None:
        kwargs["driver"] = "ipnet"

    mounts = [] if kwargs["mount"] is None else list(kwargs["mount"])

    container_config = {
        "name": random_name() if kwargs["name"] is None else kwargs["name"],
        "image": kwargs["image"],
        "cmd": list(kwargs["command"]),
        "user": kwargs["user"],
        "env": list(kwargs["env"]),
        "mounts": [decode_mount(mnt) for mnt in mounts],
        "jail_param": list(kwargs["jailparam"]),
        "persist": kwargs["persist"],
        "restart_policy": kwargs["restart"],
        "network_driver": kwargs["driver"],
        "public_ports": list(decode_public_ports(kwargs["publish"])),
    }

    try:
        container_config = ContainerConfig.from_dict(container_config)
    except ValueError as error_msg:
        echo_bold(
            f"[red]Error![/red] Could not validate container configuration: {error_msg}"
        )
        sys.exit(1)

    # Create container
    response = request_and_print_response(
        container_create_endpoint,
        kwargs={"json_body": container_config},
        statuscode2printer={
            201: print_response_id,
            404: print_nothing,
            500: print_nothing,
        },
    )

    if response is None or response.status_code != 201:
        if response is not None:
            echo_error(f"could not create container: {response.parsed.message}")
            sys.exit(1)

    container_id = response.parsed.id

    if kwargs["network"] is None:
        return container_id

    # Connect to network,
    kwargs_connect = {
        "ip": kwargs["ip"],
        "ip6": kwargs["ip6"],
        "network": kwargs["network"],
        "container": container_id,
    }
    response = _connect(**kwargs_connect)
    if response is None or response.status_code != 204:
        echo_error(f"could not connect container: {response.parsed.message}")
        sys.exit(1)

    return container_id


def _print_container(response):
    containers = response.parsed

    def command_json2command_human(command):
        if command is None:
            return "Dockerfile"

        return " ".join(command)

    containers = [
        [
            c.id,
            c.name,
            print_image_column(c.image_name, c.image_tag, c.image_id),
            command_json2command_human(c.cmd),
            human_duration(c.created) + " ago",
            "[b]yes[/b]" if c.restart_policy == "on-startup" else "no",
            is_running_str(c.running),
            "" if c.jid is None else str(c.jid),
        ]
        for c in containers
    ]

    print_table(containers, CONTAINER_LIST_COLUMNS)


def _start(detach, interactive, tty, containers):
    if interactive:
        detach = False

    if not detach and len(containers) != 1:
        echo_bold(START_ONLY_ONE_CONTAINER_WHEN_ATTACHED)
    else:
        for container in containers:
            start_container = True
            _execution_create_and_start(
                container, tty, interactive, detach, start_container
            )


def _stop(containers, silent=False):
    def silent_(_):
        return ""

    if silent:
        response_200 = silent_
    else:
        response_200 = print_response_id

    for container_id in containers:
        response = request_and_print_response(
            container_stop_endpoint,
            kwargs={"container_id": container_id},
            statuscode2printer={
                200: response_200,
                304: print_response_msg,
                404: print_response_msg,
                500: print_backend_error,
            },
        )
        if response is None or response.status_code != 200:
            break


def _execution_create_and_start(
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
    response = request_and_print_response(
        exec_create_endpoint,
        kwargs={"json_body": exec_config},
        statuscode2printer={
            201: print_nothing,
            404: print_response_msg,
            500: print_backend_error,
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
    try:
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
                    # The data from stdin should be available immediately:
                    tty.setraw(sys.stdin.fileno(), when=termios.TCSANOW)
                    loop.add_reader(sys.stdin.fileno(), _send_user_input, websocket)
                closing_message = await listen_for_messages(websocket)
                if closing_message["data"] == "":
                    print_websocket_closing(closing_message, ["message"])

                else:
                    print_websocket_closing(closing_message, ["message", "data"])

            elif start_msg["msg_type"] == "error":
                print_websocket_closing(closing_message, ["message"])

            else:
                unexpected_error()

    except websockets.exceptions.ConnectionClosedError as e:
        echo_error(
            f"Kleened returned an error with error code {e.code} and reason #{e.reason}"
        )


def _send_user_input(websocket):
    tasks = []
    input_line = sys.stdin.buffer.read(1)
    task = asyncio.ensure_future(websocket.send(input_line))
    tasks.append(task)


def _close_websocket(websocket):
    async def _close_ws(websocket):
        await websocket.close(code=1000, reason="interrupted by user")

    task = asyncio.create_task(_close_ws(websocket))
    asyncio.ensure_future(task)
