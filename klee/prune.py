import click
from .utils import request_and_validate_response
from .config import config
from .richclick import print_id_list


def prune_command(docs, warning, endpoint, name, hidden=False):
    @click.command(cls=config.command_cls, name=name, hidden=hidden, help=docs)
    @click.option(
        "--force",
        "-f",
        default=False,
        is_flag=True,
        help="Do not prompt for confirmation",
    )
    def prune(force):
        if not force:
            click.echo(warning)
            click.confirm("Are you sure you want to continue?", abort=True)
        request_and_validate_response(
            endpoint,
            kwargs={},
            statuscode2messsage={200: lambda response: print_id_list(response.parsed)},
        )

    return prune
