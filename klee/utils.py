import json
import datetime
import dateutil.parser

import websockets
import httpx

from .connection import request
from .printing import (
    echo,
    echo_bold,
    print_unable_to_connect,  # Message
    unexpected_error,  # Message
    unrecognized_status_code,  # Message
)


async def listen_for_messages(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            closing_message = json.loads(websocket.close_reason)
            echo("")
            return closing_message

        echo(message, end="")


def request_and_validate_response(endpoint, kwargs, statuscode2messsage):
    try:
        response = request(endpoint, kwargs)

    except httpx.ConnectError as e:
        print_unable_to_connect(e)
        return None

    except httpx.ReadError as e:
        print_unable_to_connect(e)
        return None

    except httpx.UnsupportedProtocol as e:
        # Request URL has an unsupported protocol 'unix://' as e:
        print_unable_to_connect(e)
        return None

    if response is None:
        return None

    # Try validating the response
    try:
        return_message = statuscode2messsage[response.status_code]
    except KeyError:
        unrecognized_status_code(status_code=response.status_code)
        return response

    if callable(return_message):
        return_message = return_message(response)
        if return_message != "" and return_message is not None:
            echo_bold(return_message)
        return response

    if not isinstance(return_message, str):
        unexpected_error()

    return response


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
