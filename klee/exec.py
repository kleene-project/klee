import signal
import asyncio
import sys
import urllib
import functools

import click

from .client.api.default.exec_create import sync_detailed as exec_create
from .client.models.exec_config import ExecConfig
from .utils import listen_for_messages, request_and_validate_response
from .connection import create_websocket

WS_EXEC_START_ENDPOINT = "/exec/{exec_id}/start?{options}"


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
        # print("YIE", endpoint)
        if attach:
            endpoint = _build_endpoint(
                exec_id, attach=True, start_container=start_container
            )
            asyncio.run(_attached_execute(endpoint, interactive))
        else:
            endpoint = _build_endpoint(
                exec_id, attach=False, start_container=start_container
            )
            asyncio.run(_execute(endpoint))


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
        click.echo(f"created execution instance {response.parsed.id}")
        return response.parsed.id

    click.echo(f"{container_id}: error creating execution instance: {response.parsed}")
    return None


async def _execute(endpoint):
    async with create_websocket(endpoint) as websocket:
        await websocket.wait_closed()
        if websocket.close_code != 1001:
            click.echo("error starting container #{container_id}")


async def _attached_execute(endpoint, interactive):
    loop = asyncio.get_running_loop()
    async with create_websocket(endpoint) as websocket:
        if interactive:
            for signame in ["SIGINT", "SIGTERM"]:
                loop.add_signal_handler(
                    getattr(signal, signame),
                    functools.partial(_close_websocket, websocket),
                )

        hello_msg = await websocket.recv()

        if hello_msg == "OK":
            if interactive:
                loop = asyncio.get_event_loop()
                loop.add_reader(sys.stdin, _send_user_input, websocket)
            await listen_for_messages(websocket)

        elif hello_msg[:6] == "ERROR:":
            click.echo(hello_msg[6:])
            await listen_for_messages(websocket)

        else:
            click.echo("error starting container #{container_id}")


def _build_endpoint(exec_id, attach, start_container):
    attach = "true" if attach else "false"
    start_container = "true" if start_container else "false"
    return WS_EXEC_START_ENDPOINT.format(
        exec_id=exec_id,
        options=urllib.parse.urlencode(
            {"attach": attach, "start_container": start_container}
        ),
    )


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
