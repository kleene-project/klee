import click

from .client.api.default.container_create import sync_detailed as container_create
from .client.models.container_config import ContainerConfig
from .container import start_container, start_attached_container
from .name_generator import random_name

from .utils import request_and_validate_response


@click.command(name="run", context_settings={"ignore_unknown_options": True})
@click.option("--name", default="", help="Assign a name to the container")
@click.option(
    "--user",
    "-u",
    default="",
    help="Alternate user that should be used for starting the container",
)
@click.option(
    "--network",
    "-n",
    multiple=True,
    default=None,
    help="Connect a container to a network",
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
@click.argument("image", nargs=1)
@click.argument("command", nargs=-1)
def run(name, user, network, volume, env, jailparam, attach, image, command):
    """Create a new container"""
    container_config = {
        "cmd": list(command),
        "networks": list(network),
        "volumes": list(volume),
        "image": image,
        "jail_param": list(jailparam),
        "env": list(env),
        "user": user,
    }
    name = random_name()
    container_config = ContainerConfig.from_dict(container_config)

    response = request_and_validate_response(
        container_create,
        kwargs={"json_body": container_config, "name": name},
        statuscode2messsage={
            201: lambda response: response.parsed.id,
            404: lambda response: response.parsed.message,
            500: lambda response: response.parsed,
        },
    )
    if response is None or response.status_code != 201:
        return

    if attach:
        start_attached_container(response.parsed.id)

    else:
        start_container(response.parsed.id)
