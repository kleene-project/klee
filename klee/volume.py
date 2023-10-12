import click

from .client.api.default.volume_create import sync_detailed as volume_create
from .client.api.default.volume_list import sync_detailed as volume_list
from .client.api.default.volume_remove import sync_detailed as volume_remove
from .client.models.volume_config import VolumeConfig
from .richclick import print_table, RichCommand, RichGroup
from .config import config
from .utils import human_duration, request_and_validate_response

# pylint: disable=unused-argument
@click.group(cls=config.group_cls)
def root(name="volume"):
    """Manage volumes"""


@root.command(cls=config.command_cls)
@click.argument("volume_name", nargs=1)
def create(volume_name):
    """
    Create a new volume. If the volume name already exists nothing happens.
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


@root.command(cls=config.command_cls, name="ls")
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


VOLUME_LIST_COLUMNS = [
    ("VOLUME NAME", {"style": "bold aquamarine1"}),
    ("CREATED", {"style": "bright_white"}),
]


def _print_volumes(volumes):
    volumes = [[vol.name, human_duration(vol.created) + "ago"] for vol in volumes]
    print_table(volumes, VOLUME_LIST_COLUMNS)


@root.command(cls=config.command_cls, name="rm")
@click.argument("volumes", required=True, nargs=-1)
def remove(volumes):
    """Remove one or more volumes. You cannot remove a volume that is in use by a container."""
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
