import click
from .client.api.default.image_list import sync_detailed as image_list
from .client.api.default.image_remove import sync_detailed as image_remove

from .utils import request_and_validate_response, human_duration


# pylint: disable=unused-argument
@click.group()
def root(name="image"):
    """Manage images"""


@root.command()
@click.option('--file', '-f', default="Dockerfile", help="Name of the Dockerfile (default: 'Dockerfile')")
@click.option('--tag', '-t', default="", help="Name and optionally a tag in the 'name:tag' format")
@click.option('--quiet', '-q', multiple=True, default=None, help="Suppress the build output and print image ID on success (default: false)")
@click.argument("path", nargs=1)
def build(file_, tag, quiet, path):
    """Build an image from a context + Dockerfile located in PATH"""
    # TODO: implement this with websockets
    click.echo("Running 'image CREATE' command")


@root.command(name="ls")
def list_images():
    """List images"""
    request_and_validate_response(
        image_list,
        kwargs = {},
        statuscode2messsage = {
            200:lambda response:_print_images(response.parsed),
            500:"jocker engine server error"
        }
    )


def _print_images(images):
    from tabulate import tabulate

    headers = ["NAME", "TAG", "ID", "CREATED"]
    containers = [
        [img.name, img.tag, img.id, human_duration(img.created)]
        for img in images
    ]

    lines = tabulate(containers, headers=headers).split("\n")
    for line in lines:
        click.echo(line)


@root.command(name="rm")
@click.argument("images", required=True, nargs=-1)
def remove(images):
    """Remove one or more images"""
    for image_id in images:
        response = request_and_validate_response(
            image_remove,
            kwargs = {"image_id": image_id},
            statuscode2messsage = {
                200:lambda response:response.parsed.id,
                404:lambda response:response.parsed.message,
                500:"jocker engine server error"
            }
        )
        if response is None or response.status_code != 200:
            break
