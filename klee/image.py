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
from .richclick import console, print_table, print_json, print_id_list
from .config import config
from .inspect import inspect_command
from .utils import (
    print_closing,
    KLEE_MSG,
    CONNECTION_CLOSED_UNEXPECTEDLY,
    UNEXPECTED_ERROR,
    human_duration,
    listen_for_messages,
    request_and_validate_response,
)


WS_IMAGE_BUILD_ENDPOINT = "/images/build"
WS_IMAGE_CREATE_ENDPOINT = "/images/create"

IMAGE_LIST_COLUMNS = [
    ("ID", {"style": "cyan"}),
    ("NAME", {"style": "bold aquamarine1"}),
    ("TAG", {"style": "aquamarine1"}),
    ("CREATED", {"style": "bright_white"}),
]

BUILD_START_MESSAGE = "[bold]Started to build image with ID {image_id}[/bold]"
BUILD_FAILED = "Failed to build image {image_id}. Last valid snapshot is {snapshot}"


# pylint: disable=unused-argument
# @click.group(cls=config.test_cls, name="image")
@click.group(cls=config.group_cls)
def root(name="image"):
    """Manage images"""


@root.group(cls=config.group_cls)
def create(name="create"):
    """
    Create a base image from a remote tar-archive or a ZFS dataset using the subcommands
    listed below.

    See the documentation for details on base images and how to create them.
    """


@create.command(cls=config.command_cls)
@click.option(
    "--tag", "-t", default="", help="Name and optionally a tag in the 'name:tag' format"
)
@click.option(
    "--url",
    "-u",
    default="",
    help="URL to a tar-archive of the userland that the image should be created from. If no url is supplied kleened will try and fetch the userland from a FreeBSD mirror.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Proceed using a userland from a FreeBSD mirror even if a customized build is detected on the kleened host.",
)
def fetch(tag, url, force):
    """
    Create a base image from a tar-archive fetched using `fetch(1)`.

    Fetch and create a base image from a tar-archive downloaded with `fetch(1)`.
    If no url is provided, kleened will download a base system from the official FreeBSD
    repositories based on host OS information from the `uname(1)` utility.
    """

    method = "fetch"
    dataset = ""
    asyncio.run(_create_image_and_listen_for_messages(tag, dataset, url, force, method))


@create.command(cls=config.command_cls)
@click.option(
    "--tag", "-t", default="", help="Name and optionally a tag in the 'name:tag' format"
)
@click.argument("dataset", nargs=1)
def zfs(tag, dataset):
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
    asyncio.run(_create_image_and_listen_for_messages(tag, dataset, url, force, method))


async def _create_image_and_listen_for_messages(tag, dataset, url, force, method):
    config = json.dumps(
        {
            "tag": tag,
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
                    print_closing(closing_message, ["message"])

                else:
                    print_closing(closing_message, ["message", "data"])

            elif start_msg["msg_type"] == "error":
                print_closing(closing_message, ["message"])

            else:
                console.print(UNEXPECTED_ERROR)

    except websockets.exceptions.ConnectionClosedError:
        console.print(CONNECTION_CLOSED_UNEXPECTEDLY)


def image_build(name, hidden=False):
    @click.command(
        cls=config.command_cls, name=name, hidden=hidden, short_help="Build a new image"
    )
    @click.option(
        "--file",
        "-f",
        default="Dockerfile",
        help="Alternative location of the Dockerfile. The location should be relative to `PATH` (default: 'Dockerfile')",
    )
    @click.option(
        "--tag",
        "-t",
        default="",
        help="Name and optionally a tag in the 'name:tag' format",
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
    config = json.dumps(
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
            await websocket.send(config)
            starting_frame = await websocket.recv()
            start_msg = json.loads(starting_frame)
            if start_msg["msg_type"] == "starting":
                if start_msg["data"] != "":
                    image_id = start_msg["data"]
                    msg = BUILD_START_MESSAGE.format(image_id=image_id)
                    console.print(msg)
                try:
                    closing_message = await listen_for_messages(websocket)
                except json.JSONDecodeError:
                    console.print(UNEXPECTED_ERROR)

                if closing_message["msg_type"] == "error":
                    if closing_message["data"] != "":
                        snapshot = closing_message["data"]
                        console.print(
                            BUILD_FAILED.format(snapshot=snapshot, image_id=image_id)
                        )

                elif closing_message["data"] == "":
                    console.print(KLEE_MSG.format(msg=closing_message["message"]))

                else:
                    console.print(KLEE_MSG.format(msg=closing_message["message"]))
                    console.print(KLEE_MSG.format(msg=closing_message["data"]))

            elif start_msg["msg_type"] == "error":
                console.print(KLEE_MSG.format(msg=start_msg["message"]))
            else:
                console.print(UNEXPECTED_ERROR)

    except websockets.exceptions.ConnectionClosedError:
        console.print(CONNECTION_CLOSED_UNEXPECTEDLY)


def image_list(name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
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
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
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
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
    @click.option(
        "--all", "-a", default=False, help="Remove tagged containers as well."
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
    @click.command(cls=config.command_cls, name=name, hidden=hidden)
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
