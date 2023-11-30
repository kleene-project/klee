import json
import asyncio
import os

import click
import websockets

from .client.api.default.image_list import sync_detailed as image_list_endpoint
from .client.api.default.image_remove import sync_detailed as image_remove_endpoint
from .client.api.default.image_tag import sync_detailed as image_tag_endpoint
from .client.api.default.image_inspect import sync_detailed as image_inspect_endpoint
from .client.api.default.image_prune import sync_detailed as image_prune_endpoint

from .connection import create_websocket
from .printing import (
    echo,
    echo_bold,
    group_cls,
    command_cls,
    print_table,
    print_websocket_closing,
    print_id_list,
    connection_closed_unexpectedly,
    unexpected_error,
)
from .inspect import inspect_command
from .utils import human_duration, listen_for_messages, request_and_validate_response


WS_IMAGE_BUILD_ENDPOINT = "/images/build"
WS_IMAGE_CREATE_ENDPOINT = "/images/create"

IMAGE_LIST_COLUMNS = [
    ("ID", {"style": "cyan"}),
    ("NAME", {"style": "bold aquamarine1"}),
    ("TAG", {"style": "aquamarine1"}),
    ("CREATED", {"style": "bright_white"}),
]

BUILD_START_MESSAGE = "Started to build image with ID {image_id}"
BUILD_FAILED = "Failed to build image {image_id}. Last valid snapshot is {snapshot}"


# pylint: disable=unused-argument
@click.group(cls=group_cls())
def root(name="image"):
    """Manage images"""


@root.group(cls=group_cls())
def create(name="create"):
    """
    Create a base image from a remote tar-archive or a ZFS dataset using the subcommands
    listed below.

    See the documentation for details on base images and how to create them.
    """


@create.command(
    cls=command_cls(),
    no_args_is_help=True,
    short_help="Create a base image from a local or remote tar-archive.",
)
@click.option(
    "--tag", "-t", default="", help="Name and optionally a tag in the 'name:tag' format"
)
@click.option(
    "--dns/--no-dns",
    is_flag=True,
    default=True,
    show_default=True,
    metavar="bool",
    help="Whether or not to copy `/etc/resolv.conf` from the host to the new image.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Proceed using a userland from a FreeBSD mirror even if a customized build is detected on the kleened host.",
)
@click.argument("method", nargs=1)
def fetch(tag, dns, force, method):
    """
    Fetch and create a base image from a tar-archive downloaded with `fetch(1)`.

    If `METHOD` is set to `auto`, Kleene will try to create the image from a userland (`base.txz`) fetched
    from the official FreeBSD repositories, based on the host OS information from `uname(1)`.

    Otherwise, `METHOD` should be an URL pointing to a tar-archive of the userland.
    """

    url = "" if method == "auto" else method
    fetching_method = "fetch"
    dataset = ""
    asyncio.run(
        _create_image_and_listen_for_messages(
            tag, dns, dataset, url, force, fetching_method
        )
    )


@create.command(cls=command_cls(), no_args_is_help=True)
@click.option(
    "--tag", "-t", default="", help="Name and optionally a tag in the 'name:tag' format"
)
@click.option(
    "--dns/--no-dns",
    is_flag=True,
    default=True,
    show_default=True,
    metavar="bool",
    help="Whether or not to copy `/etc/resolv.conf` from the host to the new image.",
)
@click.argument("dataset", nargs=1)
def zfs(tag, dns, dataset):
    """
    Create a base image from an existing ZFS dataset.

    Use a local zfs(8) dataset on the kleened host to create a base image.
    The dataset should contain a complete userland or application that can
    run in a jailed environement.

    See the documentation for details on, e.g., building a FreeBSD base system from source or
    using freebsd-update(8).
    """
    force = False
    url = ""
    method = "zfs"
    asyncio.run(
        _create_image_and_listen_for_messages(tag, dns, dataset, url, force, method)
    )


async def _create_image_and_listen_for_messages(tag, dns, dataset, url, force, method):
    config = json.dumps(
        {
            "tag": tag,
            "dns": dns,
            "method": method,
            "zfs_dataset": dataset,
            "url": url,
            "force": force,
        }
    )
    try:
        async with create_websocket(WS_IMAGE_CREATE_ENDPOINT) as websocket:
            await websocket.send(config)
            starting_frame = await websocket.recv()
            start_msg = json.loads(starting_frame)
            if start_msg["msg_type"] == "starting":
                closing_message = await listen_for_messages(websocket)

                if closing_message["data"] == "":
                    print_websocket_closing(closing_message, ["message"])

                else:
                    print_websocket_closing(closing_message, ["message", "data"])

            elif start_msg["msg_type"] == "error":
                print_websocket_closing(closing_message, ["message"])

            else:
                unexpected_error()

    except websockets.exceptions.ConnectionClosedError:
        connection_closed_unexpectedly()


def image_build(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        short_help="Build a new image",
    )
    @click.option(
        "--file",
        "-f",
        default="Dockerfile",
        help="Alternative location of the `Dockerfile`. The location should be relative to `PATH` (default: 'Dockerfile')",
    )
    @click.option(
        "--tag",
        "-t",
        default="",
        help="Name and optionally a tag in the `name:tag` format",
    )
    @click.option(
        "--quiet",
        "-q",
        is_flag=True,
        default=False,
        help="Suppress the build output and print image ID on success",
    )
    @click.option(
        "--cleanup/--no-cleanup",
        "-l",
        is_flag=True,
        default=True,
        help="Whether or not to remove the build-container if the build fails",
    )
    @click.option(
        "--build-arg",
        multiple=True,
        default=None,
        help="Set build-time variables (e.g. --build-arg FIRST=hello --build-arg SECOND=world)",
    )
    @click.argument("path", nargs=1)
    def build(file, tag, quiet, cleanup, build_arg, path):
        """Build an image from a context and Dockerfile located in PATH"""
        asyncio.run(
            _build_image_and_listen_for_messages(
                file, tag, quiet, cleanup, build_arg, path
            )
        )

    return build


root.add_command(image_build("build"), name="build")


async def _build_image_and_listen_for_messages(
    file_, tag, quiet, cleanup, build_arg, path
):
    quiet = "true" if quiet else "false"
    path = os.path.abspath(path)
    buildargs = {}
    for buildarg in build_arg:
        var, value = buildarg.split("=", maxsplit=1)
        buildargs[var] = value

    build_config = json.dumps(
        {
            "context": path,
            "file": file_,
            "tag": tag,
            "quiet": quiet,
            "cleanup": cleanup,
            "buildargs": buildargs,
        }
    )
    try:
        async with create_websocket(WS_IMAGE_BUILD_ENDPOINT) as websocket:
            await websocket.send(build_config)
            starting_frame = await websocket.recv()
            start_msg = json.loads(starting_frame)
            if start_msg["msg_type"] == "starting":
                if start_msg["data"] != "":
                    image_id = start_msg["data"]
                    echo_bold(BUILD_START_MESSAGE.format(image_id=image_id))
                try:
                    closing_message = await listen_for_messages(websocket)
                except json.JSONDecodeError:
                    unexpected_error()

                if closing_message["msg_type"] == "error":
                    if closing_message["data"] != "":
                        snapshot = closing_message["data"]
                        echo_bold(
                            BUILD_FAILED.format(snapshot=snapshot, image_id=image_id)
                        )

                elif closing_message["data"] == "":
                    echo_bold(closing_message["message"])

                else:
                    echo_bold(closing_message["message"])
                    echo_bold(closing_message["data"])

            elif start_msg["msg_type"] == "error":
                echo_bold(start_msg["message"])
            else:
                unexpected_error()

    except websockets.exceptions.ConnectionClosedError:
        connection_closed_unexpectedly()


def image_list(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
    def _image_list():
        """List images"""
        request_and_validate_response(
            image_list_endpoint,
            kwargs={},
            statuscode2messsage={
                200: lambda response: _print_image_list(response.parsed),
                500: "kleened backend error",
            },
        )

    return _image_list


root.add_command(image_list("ls"), name="ls")


def _print_image_list(images):
    images = [
        [img.id, img.name, img.tag, human_duration(img.created) + " ago"]
        for img in images
    ]
    print_table(images, IMAGE_LIST_COLUMNS)


root.add_command(
    inspect_command(
        name="inspect",
        argument="image",
        id_var="image_id",
        docs="Display detailed information on an image.",
        endpoint=image_inspect_endpoint,
    ),
    name="inspect",
)


def image_remove(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("images", required=True, nargs=-1)
    def remove(images):
        """Remove one or more images"""
        for image_id in images:
            response = request_and_validate_response(
                image_remove_endpoint,
                kwargs={"image_id": image_id},
                statuscode2messsage={
                    200: lambda response: response.parsed.id,
                    404: lambda response: response.parsed.message,
                    500: "kleened backend error",
                },
            )
            if response is None or response.status_code != 200:
                break

    return remove


root.add_command(image_remove("rm"), name="rm")


def image_prune(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
    @click.option(
        "--all",
        "-a",
        default=False,
        is_flag=True,
        help="Remove tagged containers as well.",
    )
    @click.option(
        "--force",
        "-f",
        default=False,
        is_flag=True,
        help="Do not prompt for confirmation",
    )
    def prune(**kwargs):
        """Remove images that are not being used by containers."""
        if not kwargs["force"]:
            click.echo("WARNING! This will remove all unused images.")
            click.confirm("Are you sure you want to continue?", abort=True)
        request_and_validate_response(
            image_prune_endpoint,
            kwargs={"all_": kwargs["all"]},
            statuscode2messsage={200: lambda response: print_id_list(response.parsed)},
        )

    return prune


root.add_command(image_prune("prune"), name="prune")


def image_tag(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("source_image", nargs=1)
    @click.argument("nametag", nargs=1)
    def tag(source_image, nametag):
        """
        Update the tag of image **SOURCE_IMAGE** to **NAMETAG**.

        **NAMETAG** uses the `name:tag` format. If `:tag` is omitted, `:latest` is used.
        """
        request_and_validate_response(
            image_tag_endpoint,
            kwargs={"image_id": source_image, "nametag": nametag},
            statuscode2messsage={
                200: lambda response: response.parsed.id,
                404: lambda response: response.parsed.message,
                500: "kleened backend error",
            },
        )

    return tag


root.add_command(image_tag("tag"), name="tag")
