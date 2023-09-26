import json
import signal
import asyncio
import sys
import urllib
import functools

import click

from .client.api.default.exec_create import sync_detailed as exec_create
from .client.models.exec_config import ExecConfig
from .utils import (
    listen_for_messages,
    request_and_validate_response,
    console,
    print_table,
    print_closing,
    KLEE_MSG,
    CONNECTION_CLOSED_UNEXPECTEDLY,
    UNEXPECTED_ERROR,
)
from .connection import create_websocket

WS_EXEC_START_ENDPOINT = "/exec/start"

EXEC_INSTANCE_CREATE_ERROR = KLEE_MSG.format(
    msg="{container_id}: error creating execution instance: {exec_id}"
)
EXEC_INSTANCE_CREATED = KLEE_MSG.format(msg="created execution instance {exec_id}")
ERROR_STARTING_CONTAINER = KLEE_MSG.format(msg="error starting container")


@click.command(name="exec")
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
@click.option("--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY")
@click.option("--user", "-u", default="", help="Username or UID of the executing user")
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
        exec_create,
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
            console.print(ERROR_STARTING_CONTAINER)


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
