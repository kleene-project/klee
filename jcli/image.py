import asyncio
import urllib.parse

import click
import websockets

from .client.api.default.image_list import sync_detailed as image_list
from .client.api.default.image_remove import sync_detailed as image_remove
from .utils import (
    WS_IMAGE_BUILD_URL,
    human_duration,
    listen_for_messages,
    request_and_validate_response,
)


# pylint: disable=unused-argument
@click.group()
def root(name="image"):
    """Manage images"""


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
@click.argument("path", nargs=1)
def build(file, tag, quiet, path):
    """Build an image from a context + Dockerfile located in PATH"""
    asyncio.run(_build_image_and_listen_for_messages(file, tag, quiet, path))


async def _build_image_and_listen_for_messages(file_, tag, quiet, path):
    quiet = "true" if quiet else "false"
    endpoint = WS_IMAGE_BUILD_URL.format(
        options=urllib.parse.urlencode(
            {"context": path, "file": file_, "tag": tag, "quiet": quiet}
        )
    )
    async with websockets.connect(endpoint) as websocket:
        hello_msg = await websocket.recv()
        if hello_msg == "OK":
            await listen_for_messages(websocket)
        else:
            click.echo("error building image")


@root.command(name="ls")
def list_images():
    """List images"""
    request_and_validate_response(
        image_list,
        kwargs={},
        statuscode2messsage={
            200: lambda response: _print_images(response.parsed),
            500: "jocker engine server error",
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
                500: "jocker engine server error",
            },
        )
        if response is None or response.status_code != 200:
            break


def _print_images(images):
    from tabulate import tabulate

    headers = ["ID", "NAME", "TAG", "CREATED"]
    containers = [
        [img.id, img.name, img.tag, human_duration(img.created)] for img in images
    ]

    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)
