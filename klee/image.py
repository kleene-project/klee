import json
import asyncio
import os
import sys

import click
import websockets

from .client.api.default.image_list import sync_detailed as image_list_endpoint
from .client.api.default.image_remove import sync_detailed as image_remove_endpoint
from .client.api.default.image_tag import sync_detailed as image_tag_endpoint
from .client.api.default.image_inspect import sync_detailed as image_inspect_endpoint
from .client.api.default.image_prune import sync_detailed as image_prune_endpoint
from .client.models.end_point_config import EndPointConfig

from .connection import create_websocket
from .printing import (
    echo,
    echo_bold,
    echo_error,
    group_cls,
    command_cls,
    print_table,
    print_websocket_closing,
    print_response_msg,
    print_response_id,
    print_backend_error,
    print_id_list,
    connection_closed_unexpectedly,
    unexpected_error,
)
from .inspect import inspect_command
from .utils import (
    human_duration,
    listen_for_messages,
    request_and_print_response,
    decode_mount,
)
from .name_generator import random_name
from .options import container_create_options


WS_IMAGE_BUILD_ENDPOINT = "/images/build"
WS_IMAGE_CREATE_ENDPOINT = "/images/create"

IMAGE_LIST_COLUMNS = [
    ("ID", {"style": "cyan"}),
    ("NAME", {"style": "bold aquamarine1"}),
    ("TAG", {"style": "aquamarine1"}),
    ("CREATED", {"style": "bright_white"}),
]

BUILD_START_MESSAGE = "Started to build image with ID {image_id}"
BUILD_FAILED = "Failed to build image {image_id}. Most recent snapshot is {snapshot}"


# pylint: disable=unused-argument
@click.group(cls=group_cls())
def root(name="image"):
    """Manage images"""


def image_create(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        short_help="Create a new base image",
    )
    @click.option(
        "--tag",
        "-t",
        default="",
        help="Name and optionally a tag in the 'name:tag' format",
    )
    @click.option(
        "--dns/--no-dns",
        is_flag=True,
        default=True,
        show_default=True,
        metavar="bool",
        help="Whether or not to copy /etc/resolv.conf from the host to the new image.",
    )
    @click.option(
        "--localtime/--no-localtime",
        default=True,
        show_default=True,
        metavar="bool",
        help="Whether or not to copy /etc/localtime from the host to the new image, if it exists.",
    )
    @click.option(
        "--update/--no-update",
        default=False,
        show_default=True,
        metavar="bool",
        help="Update the userland using freebsd-update(8). See the freebsd-update man-page for details on which FreeBSD versions can be updated.",
    )
    @click.option(
        "--autotag/--no-autotag",
        "-a",
        is_flag=True,
        default=True,
        show_default=True,
        metavar="bool",
        help="Autogenerate a nametag 'FreeBSD-\<version\>:latest'. If `tag` is set this is ignored. Method **fetch-auto** only.",
    )
    @click.argument("method", nargs=1)
    @click.argument("source", nargs=-1)
    def create(tag, dns, localtime, update, autotag, method, source):
        """
        Create a base image from a tar-archive or a ZFS dataset.

        **METHOD** can be one of the following:

        - **fetch-auto**: Automatically fetch a release/snapshot from the offical FreeBSD
          mirrors, based on host information from uname(1). **SOURCE** is not used.
        - **fetch**: Fetch a custom version of the base system and use it for image creation.
          **SOURCE** is a valid url for fetch(1), pointing to a base.txz file locally or remote.
        - **zfs-copy**: Create a base image from a copy of an existing ZFS dataset. **SOURCE** is the dataset.
        - **zfs-clone**: Create a base image from a clone of an existing ZFS dataset. **SOURCE** is the dataset.
        """
        _create(tag, dns, localtime, update, autotag, method, source)

    return create


def image_build(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        short_help="Build a new image",
    )
    def build(**kwargs):
        """
        Build a new image from a context and Dockerfile located in **PATH**.

        The container-related options configures the build-container.
        Note that `user` and `env` options will be overwritten by the 'USER' and 'ENV'
        Dockerfile instructions, respectively.
        """
        asyncio.run(_build_image_and_listen_for_messages(**kwargs))

    def remove_irrelevant_options(option):
        return option.name not in ("persist", "restart")

    container_options = list(
        filter(remove_irrelevant_options, container_create_options())
    )
    build.params.extend(container_options)
    build_options = [
        click.Option(
            ["--from"],
            default=None,
            help="Specify an image that will overwrite the image in the Dockerfile's 'FROM' instruction.",
        ),
        click.Option(
            ["--file", "-f"],
            default="Dockerfile",
            show_default=True,
            help="Location of the Dockerfile relative to **PATH**.",
        ),
        click.Option(
            ["--tag", "-t"],
            default="",
            help="Name and optionally a tag in the 'name:tag' format",
        ),
        click.Option(
            ["--quiet", "-q"],
            is_flag=True,
            default=False,
            metavar="flag",
            help="Suppress the build output and print image ID on success",
        ),
        click.Option(
            ["--rm"],
            is_flag=True,
            default=False,
            metavar="flag",
            help="Whether or not to remove the image if the build fails",
        ),
        click.Option(
            ["--build-arg"],
            multiple=True,
            default=None,
            metavar="list",
            help="Set build-time variables (e.g. `--build-arg FIRST=hello --build-arg SECOND=world`)",
        ),
        click.Argument(["path"], nargs=1),
    ]
    build.params.extend(build_options)

    return build


def image_list(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
    def _image_list():
        """List images"""
        request_and_print_response(
            image_list_endpoint,
            kwargs={},
            statuscode2printer={200: _print_image_list, 500: print_backend_error},
        )

    return _image_list


def image_remove(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden, no_args_is_help=True)
    @click.argument("images", required=True, nargs=-1)
    def remove(images):
        """Remove one or more images"""
        for image_id in images:
            response = request_and_print_response(
                image_remove_endpoint,
                kwargs={"image_id": image_id},
                statuscode2printer={
                    200: print_response_id,
                    404: print_response_msg,
                    500: print_backend_error,
                },
            )
            if response is None or response.status_code != 200:
                sys.exit(1)

    return remove


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
        """Remove images that are not being used by containers"""
        if not kwargs["force"]:
            click.echo("WARNING! This will remove all unused images.")
            click.confirm("Are you sure you want to continue?", abort=True)
        request_and_print_response(
            image_prune_endpoint,
            kwargs={"all_": kwargs["all"]},
            statuscode2printer={200: print_id_list},
        )

    return prune


def image_tag(name, hidden=False):
    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        no_args_is_help=True,
        short_help="Rename an image",
    )
    @click.argument("source_image", nargs=1)
    @click.argument("nametag", nargs=1)
    def tag(source_image, nametag):
        """
        Update the tag of image **SOURCE_IMAGE** to **NAMETAG**.

        **NAMETAG** uses the `name:tag` format. If `:tag` is omitted, `:latest` is used.
        """
        request_and_print_response(
            image_tag_endpoint,
            kwargs={"image_id": source_image, "nametag": nametag},
            statuscode2printer={
                200: print_response_id,
                404: print_response_msg,
                500: print_backend_error,
            },
        )

    return tag


def image_inspect(name, hidden=False):
    return inspect_command(
        name=name,
        hidden=hidden,
        argument="image",
        id_var="image_id",
        docs="Display detailed information on an image",
        endpoint=image_inspect_endpoint,
    )


root.add_command(image_create("create"), name="create")
root.add_command(image_build("build"), name="build")
root.add_command(image_list("ls"), name="ls")
root.add_command(image_inspect("inspect"), name="inspect")
root.add_command(image_remove("rm"), name="rm")
root.add_command(image_prune("prune"), name="prune")
root.add_command(image_tag("tag"), name="tag")


def _create(tag, dns, localtime, update, autotag, method, source):
    dataset = ""
    url = ""

    if len(source) > 1:
        additional_arguments = " ".join(source[1:])
        echo_error(f"too many arguments: {additional_arguments}")
        return

    if method in {"zfs-clone", "zfs-copy"}:
        dataset = source[0]

    if method == "fetch":
        url = source[0]

    if method == "fetch-auto":
        url = ""
        if tag != "":
            autotag = False

    config = {
        "method": method,
        "url": url,
        "zfs_dataset": dataset,
        "tag": tag,
        "dns": dns,
        "localtime": localtime,
        "update": update,
        "autotag": autotag,
    }
    config_json = json.dumps(config)
    asyncio.run(_create_image_and_listen_for_messages(config_json))


async def _create_image_and_listen_for_messages(config_json):
    try:
        async with create_websocket(WS_IMAGE_CREATE_ENDPOINT) as websocket:
            await websocket.send(config_json)
            starting_frame = await websocket.recv()
            start_msg = json.loads(starting_frame)
            if start_msg["msg_type"] == "starting":
                try:
                    closing_message = await listen_for_messages(websocket)
                except json.decoder.JSONDecodeError:
                    echo_error("Kleened returned an unknown error")
                    return

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


def process_build_messages(message):
    snapshot_message = "--> Snapshot created: @"
    if snapshot_message in message:
        echo_bold(message)

    elif "Step " in message and " : " in message:
        echo_bold(message)

    elif "Using user-supplied parent image:" in message:
        echo_bold(message)

    else:
        echo(message, newline=False)


async def _build_image_and_listen_for_messages(**kwargs):
    quiet = "true" if kwargs["quiet"] else "false"
    network_driver = kwargs["driver"] if kwargs["driver"] is not None else "host"
    path = os.path.abspath(kwargs["path"])
    buildargs = {}
    for buildarg in kwargs["build_arg"]:
        var, value = buildarg.split("=", maxsplit=1)
        buildargs[var] = value

    mounts = [] if kwargs["mount"] is None else list(kwargs["mount"])
    container_config = {
        "name": None,
        "cmd": None,
        "image": kwargs["from"],
        "user": kwargs["user"],
        "env": list(kwargs["env"]),
        "mounts": [decode_mount(mnt) for mnt in mounts],
        "jail_param": list(kwargs["jailparam"]),
        "network_driver": network_driver,
    }

    ip = "<auto>" if kwargs["ip"] is None else kwargs["ip"]
    ip6 = "<auto>" if kwargs["ip6"] is None else kwargs["ip6"]

    if kwargs["network"] is not None:
        container_config["network_driver"] = _default_if_none(kwargs, "driver", "ipnet")
        networks = [
            EndPointConfig.from_dict(
                {
                    "container": "",
                    "network": kwargs["network"],
                    "ip_address": ip,
                    "ip_address6": ip6,
                }
            )
        ]
    else:
        container_config["network_driver"] = _default_if_none(kwargs, "driver", "host")
        networks = []

    build_config = json.dumps(
        {
            "context": path,
            "dockerfile": kwargs["file"],
            "tag": kwargs["tag"],
            "quiet": quiet,
            "cleanup": kwargs["rm"],
            "buildargs": buildargs,
            "container_config": container_config,
            "networks": networks,
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
                    closing_message = await listen_for_messages(
                        websocket, message_processor=process_build_messages
                    )
                except json.JSONDecodeError:
                    unexpected_error()
                    sys.exit(1)

                if closing_message["msg_type"] == "error":
                    if closing_message["data"] != "":
                        snapshot = closing_message["data"]
                        echo_bold(
                            BUILD_FAILED.format(snapshot=snapshot, image_id=image_id)
                        )
                    sys.exit(1)

                elif closing_message["data"] == "":
                    echo_bold(closing_message["message"])

                else:
                    echo_bold(closing_message["message"])
                    echo_bold(closing_message["data"])

            elif start_msg["msg_type"] == "error":
                echo_bold(start_msg["message"])
                sys.exit(1)
            else:
                unexpected_error()
                sys.exit(1)

    except websockets.exceptions.ConnectionClosedError:
        connection_closed_unexpectedly()


def _default_if_none(kwargs, key, default):
    if kwargs[key] is None:
        kwargs[key] = default

    return kwargs[key]


def _print_image_list(response):
    images = [
        [img.id, img.name, img.tag, human_duration(img.created) + " ago"]
        for img in response.parsed
    ]
    print_table(images, IMAGE_LIST_COLUMNS)
