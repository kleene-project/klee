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
from .network import connect_
from .printing import (
    echo_bold,
    echo_error,
    command_cls,
    group_cls,
    print_websocket_closing,
    print_image_column,
    is_running_str,
    print_table,
    unexpected_error,
)
from .name_generator import random_name
from .connection import create_websocket
from .utils import human_duration, request_and_validate_response, listen_for_messages
from .prune import prune_command
from .inspect import inspect_command
from .options import container_create_options, exec_options

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
        `<image_id>|[<image_name>[:<tag>]][@<snapshot_id>]`

        See the documentation for details.
        """
        _create_container_and_connect_to_network(**kwargs)

    create = container_create_options(create)
    create.params.extend(
        [click.Argument(["image"], nargs=1), click.Argument(["command"], nargs=-1)]
    )
    return create


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
                help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)",
            ),
            click.Option(
                ["--user", "-u"],
                default="",
                help="Username or UID of the executing user",
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

    run = container_create_options(run)
    run = exec_options(run)
    run.params.extend(
        [click.Argument(["image"], nargs=1), click.Argument(["command"], nargs=-1)]
    )
    return run


root.add_command(container_create("create"), name="create")
root.add_command(container_list("ls"), name="ls")
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
    kwargs_create = {
        "name": random_name() if kwargs["name"] is None else kwargs["name"],
        "image": kwargs["image"],
        "command": kwargs["command"],
        "user": kwargs["user"],
        "mount": kwargs["mount"],
        "env": kwargs["env"],
        "jailparam": kwargs["jailparam"],
        "network_driver": kwargs["driver"],
    }

    kwargs_create["public_ports"] = list(_decode_public_ports(kwargs["publish"]))

    response = _create(**kwargs_create)

    if response is None or response.status_code != 201:
        if response is not None:
            echo_error(f"could not create container: {response.parsed.message}")
        return None

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
        return None

    return container_id


def _decode_public_ports(public_ports):
    """
    Decodes
    - <HOST-PORT>[:CONTAINER-PORT][/<PROTOCOL>] and
    - <INTERFACE>:<HOST-PORT>:<CONTAINER-PORT>[/<PROTOCOL>]
    """
    for pub_port in public_ports:
        pub_port, protocol = _extract_protocol(pub_port)
        interfaces, host_port, container_port = _extract_ports_and_interface(pub_port)
        yield {
            "interfaces": interfaces,
            "host_port": host_port,
            "container_port": container_port,
            "protocol": protocol,
        }


def _extract_protocol(pub_port_raw):
    pub_port = pub_port_raw.split("/")
    if len(pub_port) == 2:
        return pub_port[0], pub_port[1]

    if len(pub_port) == 1:
        return pub_port[0], "tcp"

    echo_error("could not decode port to publish: ", pub_port_raw)
    sys.exit(1)


def _extract_ports_and_interface(pub_port_raw):
    pub_port = pub_port_raw.split(":")
    if len(pub_port) == 3:
        return [pub_port[0]], pub_port[1], pub_port[2]

    if len(pub_port) == 2:
        return [], pub_port[0], pub_port[1]

    if len(pub_port) == 1:
        return [], pub_port[0], pub_port[0]

    echo_error("could not decode port to publish: ", pub_port_raw)
    sys.exit(1)


def _create(**kwargs):
    mounts = [] if kwargs["mount"] is None else list(kwargs["mount"])

    container_config = {
        "name": kwargs["name"],
        "image": kwargs["image"],
        "cmd": list(kwargs["command"]),
        "user": kwargs["user"],
        "env": list(kwargs["env"]),
        "mounts": [_decode_mount(mnt) for mnt in mounts],
        "jail_param": list(kwargs["jailparam"]),
        "network_driver": kwargs["network_driver"],
        "public_ports": kwargs["public_ports"],
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


def _decode_mount(mount):
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


def _print_container(response):
    containers = response.parsed

    def command_json2command_human(command_str):
        return " ".join(json.loads(command_str))

    containers = [
        [
            c.id,
            c.name,
            print_image_column(c.image_name, c.image_tag, c.image_id),
            command_json2command_human(c.cmd),
            human_duration(c.created) + " ago",
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
