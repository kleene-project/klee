import sys
import json
import datetime
import dateutil.parser

import websockets
import httpx

from .connection import request
from .printing import (
    echo,
    echo_bold,
    echo_error,
    print_unable_to_connect,  # Message
    print_timeout,
    unexpected_error,  # Message
    unrecognized_status_code,  # Message
    print_unexpected_response,
)


async def listen_for_messages(websocket, newline=False, message_processor=None):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            closing_message = json.loads(websocket.close_reason)
            echo("")
            return closing_message

        if message_processor is None:
            echo(message, newline)
        else:
            message_processor(message)


def request_and_print_response(endpoint, kwargs, statuscode2printer):
    try:
        response = request(endpoint, kwargs)

    except httpx.ConnectError as e:
        print_unable_to_connect(e)
        sys.exit(1)

    except httpx.ReadError as e:
        print_unable_to_connect(e)
        sys.exit(1)

    except httpx.UnsupportedProtocol as e:
        # Request URL has an unsupported protocol 'unix://' as e:
        print_unable_to_connect(e)
        sys.exit(1)

    except httpx.ReadTimeout:
        print_timeout()
        sys.exit(1)

    except json.decoder.JSONDecodeError:
        print_unexpected_response()
        sys.exit(1)

    if response is None:
        return None

    try:
        message_printer = statuscode2printer[response.status_code]
    except KeyError:
        unrecognized_status_code(status_code=response.status_code)
        return response

    message_printer(response)

    return response


def decode_mount(mount):
    sections = mount.split(":")
    if len(sections) > 3:
        echo_error(f"invalid mount format '{mount}'. Max 3 elements seperated by ':'.")
        sys.exit(125)

    if len(sections) < 2:
        echo_error(
            f"invalid mount format '{mount}'. Must have at least 2 elements seperated by ':'."
        )
        sys.exit(125)

    if len(sections) == 3 and sections[-1] not in {"ro", "rw"}:
        echo_error(
            f"invalid mount format '{mount}'. Last element should be either 'ro' or 'rw'."
        )
        sys.exit(125)

    if len(sections) == 3:
        source, destination, mode = sections
        read_only = True if mode == "ro" else False
    else:
        source, destination = sections
        read_only = False

    if source[:1] == "/":
        mount_type = "nullfs"
    else:
        mount_type = "volume"

    return {
        "type": mount_type,
        "source": source,
        "destination": destination,
        "read_only": read_only,
    }


def decode_public_ports(public_ports):
    """
    Decodes
    - <HOST-PORT>[:CONTAINER-PORT][/<PROTOCOL>] and
    - <INTERFACE>:<HOST-PORT>:<CONTAINER-PORT>[/<PROTOCOL>]
    """
    for pub_port in public_ports:
        pub_port, protocol = _extract_protocol(pub_port)
        interfaces, host_port, container_port = _extract_ports_and_interface(pub_port)
        yield {
            "interfaces": interfaces,
            "host_port": host_port,
            "container_port": container_port,
            "protocol": protocol,
        }


def _extract_protocol(pub_port_raw):
    pub_port = pub_port_raw.split("/")
    if len(pub_port) == 2:
        return pub_port[0], pub_port[1]

    if len(pub_port) == 1:
        return pub_port[0], "tcp"

    echo_error("could not decode port to publish: ", pub_port_raw)
    sys.exit(1)


def _extract_ports_and_interface(pub_port_raw):
    pub_port = pub_port_raw.split(":")
    if len(pub_port) == 3:
        return [pub_port[0]], pub_port[1], pub_port[2]

    if len(pub_port) == 2:
        return [], pub_port[0], pub_port[1]

    if len(pub_port) == 1:
        return [], pub_port[0], pub_port[0]

    echo_error("could not decode port to publish: ", pub_port_raw)
    sys.exit(1)


def human_duration(timestamp_iso):
    now = datetime.datetime.now().timestamp()
    timestamp = dateutil.parser.parse(timestamp_iso)
    seconds = int(now - timestamp.timestamp())
    if seconds < 1:
        return "Less than a second"
    if seconds == 1:
        return "1 second"
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = int(seconds / 60)
    if minutes == 1:
        return "About a minute"
    if minutes < 60:
        return f"{minutes} minutes"
    hours = int((minutes / 60) + 0.5)
    if hours == 1:
        return "About an hour"
    if hours < 48:
        return f"{hours} hours"
    if hours < 24 * 7 * 2:
        d = int(hours / 24)
        return f"{d} days"
    if hours < 24 * 30 * 2:
        w = int(hours / 24 / 7)
        return f"{w} weeks"
    if hours < 24 * 365 * 2:
        m = int(hours / 24 / 30)
        return f"{m} months"
    years = int(hours / 24 / 365)
    return f"{years} years"
