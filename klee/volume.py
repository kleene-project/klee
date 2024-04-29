import click

from .client.api.default.volume_create import sync_detailed as volume_create_endpoint
from .client.api.default.volume_list import sync_detailed as volume_list_endpoint
from .client.api.default.volume_inspect import sync_detailed as volume_inspect_endpoint
from .client.api.default.volume_remove import sync_detailed as volume_remove_endpoint
from .client.api.default.volume_prune import sync_detailed as volume_prune_endpoint

from .client.models.volume_config import VolumeConfig
from .printing import (
    print_table,
    command_cls,
    group_cls,
    print_response_id,
    print_response_msg,
    print_backend_error,
)
from .prune import prune_command
from .inspect import inspect_command
from .utils import human_duration, request_and_print_response

# pylint: disable=unused-argument
@click.group(cls=group_cls())
def root(name="volume"):
    """Manage volumes"""


def volume_create(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("volume_name", nargs=1)
    def create(volume_name):
        """
        Create a new volume. If the volume name already exists nothing happens.
        """
        config = VolumeConfig.from_dict({"name": volume_name})
        request_and_print_response(
            volume_create_endpoint,
            kwargs={"json_body": config},
            statuscode2printer={201: print_response_id, 500: print_backend_error},
        )

    return create


def volume_list(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
    def listing():
        """List volumes"""
        request_and_print_response(
            volume_list_endpoint,
            kwargs={},
            statuscode2printer={200: _print_volumes, 500: print_backend_error},
        )

    return listing


def _print_volumes(response):
    VOLUME_LIST_COLUMNS = [
        ("VOLUME NAME", {"style": "bold aquamarine1"}),
        ("CREATED", {"style": "bright_white"}),
    ]
    volumes = [
        [vol.name, human_duration(vol.created) + " ago"] for vol in response.parsed
    ]
    print_table(volumes, VOLUME_LIST_COLUMNS)


def volume_inspect(name, hidden=False):
    return inspect_command(
        name=name,
        hidden=hidden,
        argument="volume",
        id_var="volume_name",
        docs="Display detailed information on an volume.",
        endpoint=volume_inspect_endpoint,
    )


def volume_remove(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("volumes", required=True, nargs=-1)
    def remove(volumes):
        """Remove one or more volumes. You cannot remove a volume that is in use by a container."""
        for volume_name in volumes:
            response = request_and_print_response(
                volume_remove_endpoint,
                kwargs={"volume_name": volume_name},
                statuscode2printer={
                    200: print_response_id,
                    404: print_response_msg,
                    500: print_backend_error,
                },
            )
            if response is None or response.status_code != 200:
                break

    return remove


root.add_command(volume_create("create"), name="create")
root.add_command(volume_list("ls"), name="ls")
root.add_command(volume_inspect("inspect"), name="inspect")
root.add_command(volume_remove("rm"), name="rm")
root.add_command(
    prune_command(
        name="prune",
        docs="Remove all volumes that are not being mounted into any containers.",
        warning="WARNING! This will remove all unused volumes.",
        endpoint=volume_prune_endpoint,
    )
)
