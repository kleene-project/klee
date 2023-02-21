import click

from .client.api.default.volume_create import sync_detailed as volume_create
from .client.api.default.volume_list import sync_detailed as volume_list
from .client.api.default.volume_remove import sync_detailed as volume_remove
from .client.models.volume_config import VolumeConfig
from .utils import human_duration, request_and_validate_response


# pylint: disable=unused-argument
@click.group()
def root(name="volume"):
    """Manage volumes"""


@root.command()
@click.argument("volume_name", nargs=1)
def create(volume_name):
    """
    Create a new volume. If no volume name is provided kleened generates one.
    If the volume name already exists nothing happens.
    """
    config = VolumeConfig.from_dict({"name": volume_name})
    request_and_validate_response(
        volume_create,
        kwargs={"json_body": config},
        statuscode2messsage={
            201: lambda response: response.parsed.id,
            500: "kleened backend error",
        },
    )


@root.command(name="ls")
def list_volumes():
    """List volumes"""
    request_and_validate_response(
        volume_list,
        kwargs={},
        statuscode2messsage={
            200: lambda response: _print_volumes(response.parsed),
            500: "kleened backend error",
        },
    )


def _print_volumes(volumes):
    from tabulate import tabulate

    headers = ["VOLUME NAME", "CREATED"]
    containers = [[vol.name, human_duration(vol.created)] for vol in volumes]

    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)


@root.command(name="rm")
@click.argument("volumes", required=True, nargs=-1)
def remove(volumes):
    """Remove one or more volumes"""
    for volume_name in volumes:
        response = request_and_validate_response(
            volume_remove,
            kwargs={"volume_name": volume_name},
            statuscode2messsage={
                200: lambda response: response.parsed.id,
                404: lambda response: response.parsed.message,
                500: "kleened backend error",
            },
        )
        if response is None or response.status_code != 200:
            break
