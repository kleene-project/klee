import datetime

import click
import dateutil.parser
import websockets
import httpx

from .connection import request


async def listen_for_messages(websocket, nl=False):
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            click.echo(f"{websocket.close_reason}")
            break

        click.echo(message, nl=nl)


def request_and_validate_response(endpoint, kwargs, statuscode2messsage):
    try:
        response = request(endpoint, kwargs)
    except httpx.ConnectError as e:
        click.echo(f"unable to connect to kleened: {e}")
        return None
    except httpx.ReadError as e:
        click.echo(f"unable to connect to kleened: {e}")
        return None

    # Try validating the response
    try:
        return_message = statuscode2messsage[response.status_code]
    except KeyError:
        click.echo(f"unknown status-code received from kleened: {response.status_code}")
        return response

    if callable(return_message):
        return_message = return_message(response)
        if return_message != "":
            click.echo(return_message)
        return response

    if not isinstance(return_message, str):
        click.echo("internal error in klee")

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
