import datetime

import click
import dateutil.parser
import httpx
import websockets

from .client.client import Client

BASE_URL = "http://localhost:8085"
WS_IMAGE_BUILD_URL = "ws://localhost:8085/images/build?{options}"
WS_CONTAINER_ATTACH_URL = "ws://localhost:8085/containers/{container_id}/attach"


async def listen_for_messages(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            click.echo(f"{websocket.close_reason}")
            break

        if message[:3] == "io:":
            click.echo(message[3:])
        else:
            click.echo("unknown error while receiving container output")


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


def request_and_validate_response(endpoint, kwargs, statuscode2messsage):
    client = Client(base_url=BASE_URL)
    # Try to connect to backend
    try:
        response = endpoint(client=client, **kwargs)
    except httpx.ConnectError as e:
        click.echo(f"unable to connect to jocker engine: {e}")
        return None

    # Try validating the response
    try:
        return_message = statuscode2messsage[response.status_code]
    except KeyError:
        click.echo(
            f"unknown status-code received from jocker engine: {response.status_code}"
        )
        return response

    if callable(return_message):
        return_message = return_message(response)

    elif not isinstance(return_message, str):
        click.echo("internal error in jcli")
        return response

    if return_message != "":
        click.echo(return_message)
    return response
