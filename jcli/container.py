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
    if name == "":
        name = random_name()

    container_config = ContainerConfig.from_dict(container_config)
    client = Client(base_url=BASE_URL)
    try:
        response = container_create(client=client, json_body=container_config, name=name)
    except httpx.ConnectError as e:
        click.echo(f"unable to connect to jocker engine: {e}")
        return

    if response.status_code != 201:
        click.echo(f"Jocker engine returned unsuccesful statuscode: {response.status_code}")
    else:
        click.echo(response.parsed.id)

@root.command(name="ls")
@click.option('--all', '-a', default=False, is_flag=True, help="Show all containers (default shows only running containers)")
def list_containers(**kwargs):
    """List containers"""
    client = Client(base_url=BASE_URL)
    response = container_list(client=client, all_=kwargs["all"])

    if response.status_code != 200:
        click.echo("unknown response code received when listing container: {response.status_code}")
    else:
        _print_container(response.parsed)


def _print_container(containers):
    # containers = ContainerSummary(command='[]', created='2021-12-04T14:25:50.481283Z', id='37ba0e2a2ef3', image_id='base', image_name='', image_tag='', name='testcontainer', running=False, additional_properties={})
    from tabulate import tabulate
    headers = ["CONTAINER ID", "IMAGE", "COMMAND", "CREATED", "STATUS", "NAME"]
    containers = [
        [c.id, c.image_id, c.command, human_duration(c.created), is_running_str(c.running), c.name]
        for c in containers
    ]

    # TODO: Parse the json list from "c.command" into a single command string
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
    client = Client(base_url=BASE_URL)
    for container_id in containers:
        response = container_delete(client=client, container_id=container_id)

        if response.status_code != 200:
            click.echo(f"non-succesful response code received: {response.status_code}")
            break

        click.echo(response.parsed.id)


@root.command(name="start")
@click.option('--attach', '-a', default=False, is_flag=True, help="Attach to STDOUT/STDERR")
@click.argument("containers", required=True, nargs=-1)
def start(attach, containers):
    """Start one or more stopped containers. Attach only if a single container is started"""
    click.echo("Running 'CONTAINER START' command")
    client = Client(base_url=BASE_URL)

    if attach:
        #TODO
        click.echo("Implement me!")
        return

    for container_id in containers:
        response = container_start(client=client, container_id=container_id)

        if response.status_code != 200:
            click.echo(f"non-succesful response code received: {response.status_code}")
            break

        click.echo(response.parsed.id)



@root.command(name="stop")
@click.argument("containers", nargs=-1)
def stop(containers):
    """Stop one or more running containers"""
    click.echo("Running 'CONTAINER STOP' command")
    client = Client(base_url=BASE_URL)

    for container_id in containers:
        response = container_stop(client=client, container_id=container_id)

        if response.status_code != 200:
            click.echo(f"non-succesful response code received: {response.status_code}")
            break

        click.echo(response.parsed.id)
