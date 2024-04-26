import click

from .utils import request_and_print_response
from .printing import command_cls, print_json, print_response_msg, print_backend_error


def inspect_command(name, docs, argument, id_var, endpoint, hidden=False):
    @click.command(
        cls=command_cls(), name=name, hidden=hidden, help=docs, no_args_is_help=True
    )
    @click.argument(argument, nargs=1)
    def inspect(**kwargs):
        request_and_print_response(
            endpoint,
            kwargs={id_var: kwargs[argument]},
            statuscode2printer={
                200: print_json,
                404: print_response_msg,
                500: print_backend_error,
            },
        )

    return inspect
