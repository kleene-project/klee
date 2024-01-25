import click

from .client.api.default.volume_create import sync_detailed as volume_create
from .client.api.default.volume_list import sync_detailed as volume_list_endpoint
from .client.api.default.volume_inspect import sync_detailed as volume_inspect_endpoint
from .client.api.default.volume_remove import sync_detailed as volume_remove
from .client.api.default.volume_prune import sync_detailed as volume_prune_endpoint

from .client.models.volume_config import VolumeConfig
from .printing import print_table, command_cls, group_cls
from .prune import prune_command
from .inspect import inspect_command
from .utils import human_duration, request_and_validate_response

# pylint: disable=unused-argument
@click.group(cls=group_cls())
def root(name="volume"):
    """Manage volumes"""


@root.command(cls=command_cls(), no_args_is_help=True)
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


def volume_list(name, hidden=False):
    VOLUME_LIST_COLUMNS = [
        ("VOLUME NAME", {"style": "bold aquamarine1"}),
        ("CREATED", {"style": "bright_white"}),
    ]

    def _print_volumes(volumes):
        volumes = [[vol.name, human_duration(vol.created) + " ago"] for vol in volumes]
        print_table(volumes, VOLUME_LIST_COLUMNS)

    @root.command(cls=command_cls(), name=name, hidden=hidden)
    def listing():
        """List volumes"""
        request_and_validate_response(
            volume_list_endpoint,
            kwargs={},
            statuscode2messsage={
                200: lambda response: _print_volumes(response.parsed),
                500: "kleened backend error",
            },
        )

    return listing


root.add_command(volume_list("ls"), name="ls")

root.add_command(
    inspect_command(
        name="inspect",
        argument="volume",
        id_var="volume_name",
        docs="Display detailed information on an volume.",
        endpoint=volume_inspect_endpoint,
    ),
    name="inspect",
)


@root.command(cls=command_cls(), name="rm", no_args_is_help=True)
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


root.add_command(
    prune_command(
        name="prune",
        docs="Remove all volumes that are not being mounted into any containers.",
        warning="WARNING! This will remove all unused volumes.",
        endpoint=volume_prune_endpoint,
    )
)
