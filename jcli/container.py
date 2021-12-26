import json
import datetime
import dateutil.parser

import click
import httpx

from .client.client import Client
from .client.models.container_config import ContainerConfig
from .name_generator import random_name
from .client.api.default.container_list import sync_detailed as container_list
from .client.api.default.container_create import sync_detailed as container_create
from .client.api.default.container_delete import sync_detailed as container_delete
from .client.api.default.container_start import sync_detailed as container_start
from .client.api.default.container_stop import sync_detailed as container_stop


BASE_URL = "http://localhost:8085"


def is_running_str(running):
    if running:
        return "running"
    return "stopped"


def human_duration(timestamp_iso):
    now = datetime.datetime.now().timestamp()
    timestamp = dateutil.parser.parse(timestamp_iso)
    seconds = int(now - timestamp.timestamp())
    if seconds < 1:
        return "Less than a second"
    if seconds == 1:
        return "1 second"
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = int(seconds / 60)
    if minutes == 1:
        return "About a minute"
    if minutes < 60:
        return f"{minutes} minutes"
    hours = int((minutes / 60) + 0.5)
    if hours == 1:
        return "About an hour"
    if hours < 48:
        return f"{hours} hours"
    if hours < 24*7*2:
        d = int(hours/24)
        return f"{d} days"
    if hours < 24*30*2:
        w = int(hours/24/7)
        return f"{w} weeks"
    if hours < 24*365*2:
        m = int(hours/24/30)
        return f"{m} months"
    years = int(hours/24/365)
    return f"{years} years"


# pylint: disable=unused-argument
@click.group()
def root(name="container"):
    """Manage containers"""


@root.command(name="create")
@click.option('--name', default="", help="Assign a name to the container")
@click.option('--network', '-n', multiple=True, default=None, help="Connect a container to a network")
@click.option('--volume', '-v', multiple=True, default=None, help="Bind mount a volume to the container")
@click.option('--env', '-e', multiple=True, default=None, help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)")
@click.option('--jailparam', '-J', multiple=True, default=["mount.devfs"], show_default=True, help="Specify a jail parameters, see jail(8) for details")
@click.argument("image", nargs=1)
@click.argument("command", nargs=-1)
def create(name, network, volume, env, jailparam, image, command):
    """Create a new container"""
    container_config = {
        "cmd":list(command),
        "networks": list(network),
        "volumes": list(volume),
        "image": image,
        "jail_param": list(jailparam),
        "env": list(env),
        "user":"", # TODO: Should it be possible to override this through cli option?
    }
    container_config = ContainerConfig.from_dict(container_config)
    if name == "":
        name = random_name()


    request_and_validate_response(
        container_create,
        kwargs={
            "json_body": container_config,
            "name":name
        },
        statuscode2messsage={
            201:lambda response:response.parsed.id,
            500:"jocker engine server error"
        }
    )

@root.command(name="ls")
@click.option('--all', '-a', default=False, is_flag=True, help="Show all containers (default shows only running containers)")
def list_containers(**kwargs):
    """List containers"""
    request_and_validate_response(
        container_list,
        kwargs = {"all_": kwargs["all"]},
        statuscode2messsage = {
            200:lambda response:_print_container(response.parsed),
            500:"jocker engine server error"
        }
    )


def _command_json2command_human(command_str):
    return " ".join(json.loads(command_str))


def _print_container(containers):
    from tabulate import tabulate
    headers = ["CONTAINER ID", "IMAGE", "TAG", "COMMAND", "CREATED", "STATUS", "NAME"]
    containers = [
        [c.id, c.image_id, c.image_tag, _command_json2command_human(c.command), human_duration(c.created), is_running_str(c.running), c.name]
        for c in containers
    ]

    # TODO: The README.md says that 'maxcolwidths' exists but it complains here. Perhaps it is not in the newest version on pypi yet?
    # col_widths = [12, 15, 23, 18, 7]
    #lines = tabulate(containers, headers=headers,  maxcolwidths=col_widths).split("\n")
    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)


@root.command(name="rm")
@click.argument("containers", required=True, nargs=-1)
def remove(containers):
    """Remove one or more containers"""
    for container_id in containers:
        response = request_and_validate_response(
                container_list,
                kwargs = {"container_id": container_id},
                statuscode2messsage = {
                    200:lambda response:response.parsed.id,
                    404:lambda response:response.parsed.message,
                    500:"jocker engine server error"
                }
            )
        if response is None or response.status_code != 200:
            break


@root.command(name="start")
@click.option('--attach', '-a', default=False, is_flag=True, help="Attach to STDOUT/STDERR")
@click.argument("containers", required=True, nargs=-1)
def start(attach, containers):
    """Start one or more stopped containers. Attach only if a single container is started"""
    if attach:
        # TODO: Implement this
        click.echo("Implement me!")
        return

    for container_id in containers:
        response = request_and_validate_response(
                container_start,
                kwargs = {"container_id": container_id},
                statuscode2messsage = {
                    200:lambda response:response.parsed.id,
                    304:lambda response:response.parsed.message,
                    404:lambda response:response.parsed.message,
                    500:"jocker engine server error"
                }
            )
        if response is None or response.status_code != 200:
            break


@root.command(name="stop")
@click.argument("containers", nargs=-1)
def stop(containers):
    """Stop one or more running containers"""
    for container_id in containers:
        response = request_and_validate_response(
                container_stop,
                kwargs = {"container_id": container_id},
                statuscode2messsage = {
                    200:lambda response:response.parsed.id,
                    304:lambda response:response.parsed.message,
                    404:lambda response:response.parsed.message,
                    500:"jocker engine server error"
                }
            )
        if response is None or response.status_code != 200:
            break


def request_and_validate_response(endpoint, kwargs, statuscode2messsage):
    client = Client(base_url=BASE_URL)
    # Try to connect to backend
    try:
        response = endpoint(client=client, **kwargs)
    except httpx.ConnectError as e:
        click.echo(f"unable to connect to jocker engine: {e}")
        return None


    # Try validating the response
    try:
        return_message = statuscode2messsage[response.status_code]
    except KeyError:
        click.echo(f"unknown status-code received from jocker engine: {response.status_code}")
        return response

    if callable(return_message):
        return_message = return_message(response)

    elif not isinstance(return_message, str):
        click.echo("internal error in jcli")
        return response

    click.echo(return_message)
    return response
