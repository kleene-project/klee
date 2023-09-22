import json
import asyncio
import os

import click
import websockets

from .client.api.default.image_list import sync_detailed as image_list
from .client.api.default.image_remove import sync_detailed as image_remove
from .connection import create_websocket
from .utils import human_duration, listen_for_messages, request_and_validate_response


WS_IMAGE_BUILD_ENDPOINT = "/images/build"
WS_IMAGE_CREATE_ENDPOINT = "/images/create"
IMAGE_LIST_HEADER = ["ID", "NAME", "TAG", "CREATED"]
IMAGE_BUILD_START_MESSAGE = "started building image with ID {image_id}"


# pylint: disable=unused-argument
@click.group()
def root(name="image"):
    """Manage images"""


@root.group()
def create(name="create"):
    """
    Create a base image from a remote tar-archive or a ZFS dataset.

    The 'fetch' command can be used for creating base images from tar-archives downloaded with fetch(1).
    If no url is provided, kleened will download a base system from the official FreeBSD repositories based
    on host OS information from the uname(1) utility.

    The 'zfs' command can be used to create a base image from a zfs(8) dataset on the kleened host containing,
    e.g., a FreeBSD base system that has been built locally on the kleeened host.

    See the documentation for details.
    """


@create.command()
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
    Fetch a tar-archive and create a base image from it.
    """

    method = "fetch"
    dataset = ""
    asyncio.run(_create_image_and_listen_for_messages(tag, dataset, url, force, method))


@create.command()
@click.option(
    "--tag", "-t", default="", help="Name and optionally a tag in the 'name:tag' format"
)
@click.argument("dataset", nargs=1)
def zfs(tag, dataset):
    """
    Use a local ZFS dataset on the kleened host to create a base image.
    The dataset can be populate with, e.g., a local build of FreeBSD or using freebsd-update(8).
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
                    click.echo(closing_message["message"])

                else:
                    click.echo(closing_message["message"])
                    click.echo(closing_message["data"])

            elif start_msg["msg_type"] == "error":
                click.echo(start_msg["message"])

            else:
                click.echo("error creating image")

    except websockets.exceptions.ConnectionClosedError:
        click.echo(
            "ERROR: image creation failed unexpectantly. Failed to create image."
        )


@root.command()
@click.option(
    "--file",
    "-f",
    default="Dockerfile",
    help="Name of the Dockerfile (default: 'Dockerfile')",
)
@click.option(
    "--tag", "-t", default="", help="Name and optionally a tag in the 'name:tag' format"
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
@click.argument("path", nargs=1)
def build(file, tag, quiet, cleanup, path):
    """Build an image from a context + Dockerfile located in PATH"""
    asyncio.run(_build_image_and_listen_for_messages(file, tag, quiet, cleanup, path))


async def _build_image_and_listen_for_messages(file_, tag, quiet, cleanup, path):
    quiet = "true" if quiet else "false"
    path = os.path.abspath(path)
    config = json.dumps(
        {"context": path, "file": file_, "tag": tag, "quiet": quiet, "cleanup": cleanup}
    )
    try:
        async with create_websocket(WS_IMAGE_BUILD_ENDPOINT) as websocket:
            await websocket.send(config)
            starting_frame = await websocket.recv()
            start_msg = json.loads(starting_frame)
            if start_msg["msg_type"] == "starting":
                image_id = start_msg["data"]
                click.echo(IMAGE_BUILD_START_MESSAGE.format(image_id=image_id))
                try:
                    closing_message = await listen_for_messages(websocket)
                except json.JSONDecodeError:
                    click.echo("\nklee: some unexpected error occured")

                if closing_message["msg_type"] == "error":
                    if closing_message["data"] != "":
                        snapshot = closing_message["data"]
                        click.echo(
                            f"Failed to build image {image_id}. Last valid snapshot is {snapshot}"
                        )

                elif closing_message["data"] == "":
                    click.echo(closing_message["message"])

                else:
                    click.echo(closing_message["message"])
                    click.echo(closing_message["data"])

            elif start_msg["msg_type"] == "error":
                click.echo(start_msg["message"])
            else:
                click.echo("error building image")

    except websockets.exceptions.ConnectionClosedError:
        click.echo("ERROR: build failed unexpectantly. Failed to build image.")


@root.command(name="ls")
def list_images():
    """List images"""
    request_and_validate_response(
        image_list,
        kwargs={},
        statuscode2messsage={
            200: lambda response: _print_images(response.parsed),
            500: "kleened backend error",
        },
    )


@root.command(name="rm")
@click.argument("images", required=True, nargs=-1)
def remove(images):
    """Remove one or more images"""
    for image_id in images:
        response = request_and_validate_response(
            image_remove,
            kwargs={"image_id": image_id},
            statuscode2messsage={
                200: lambda response: response.parsed.id,
                404: lambda response: response.parsed.message,
                500: "kleened backend error",
            },
        )
        if response is None or response.status_code != 200:
            break


def _print_images(images):
    from tabulate import tabulate

    containers = [
        [img.id, img.name, img.tag, human_duration(img.created)] for img in images
    ]

    lines = tabulate(containers, headers=IMAGE_LIST_HEADER).split("\n")
    for line in lines:
        click.echo(line)
