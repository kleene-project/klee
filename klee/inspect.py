import click

from .utils import request_and_validate_response
from .config import config
from .richclick import print_json


def inspect_command(name, docs, argument, id_var, endpoint, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden, help=docs)
    @click.argument(argument, nargs=1)
    def inspect(**kwargs):
        request_and_validate_response(
            endpoint,
            kwargs={id_var: kwargs[argument]},
            statuscode2messsage={
                200: lambda response: print_json(response.parsed),
                404: lambda response: response.parsed.message,
                500: "kleened backend error",
            },
        )

    return inspect
