# """
# FROM KLEE CLI:
#  Usage:  klee [OPTIONS] COMMAND
#
#  A self-sufficient runtime for containers
#
#  Options:
#  -v, --version            Print version information and quit
#  -D, --debug              Enable debug mode
#  -H, --host string        Daemon socket to connect to: tcp://[host]:[port][path] or unix://[/path/to/socket]
#
#  Management Commands:
#  container   Manage containers
#  image       Manage images
#  network     Manage networks
#  volume      Manage volumes
#
#  Run 'klee COMMAND --help' for more information on a command.
# """

import click

from .container import root as container_root
from .image import root as image_root
from .network import root as network_root
from .run import run
from .volume import root as volume_root


@click.group()
@click.version_option(version="0.0.1")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option(
    "--host",
    default="tcp://localhost:8085",
    show_default=True,
    help="Engine socket to connect to: tcp://[host]:[port] or unix://[/path/to/socket]",
)
def cli(debug, host):
    """
    cli for the kleened backend
    """


cli.add_command(container_root, name="container")
cli.add_command(image_root, name="image")
cli.add_command(network_root, name="network")
cli.add_command(volume_root, name="volume")
cli.add_command(run, name="run")

if __name__ == "__main__":
    cli()
