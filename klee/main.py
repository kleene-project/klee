from urllib.parse import urlparse

import click

from .connection import config as connection_config
from .container import root as container_root
from .image import root as image_root
from .network import root as network_root
from .run import run
from .volume import root as volume_root


@click.group()
@click.version_option(version="0.0.1")
@click.option(
    "--host",
    default="http:///var/run/kleened.sock",
    show_default=True,
    help="Host address and protocol to use. See the docs for details.",
)
@click.option(
    "--tlsverify/--no-tlsverify",
    default=True,
    show_default=True,
    help="Verify the server cert. Uses the CA bundle provided by Certifi unless the '--cacert' is set.",
)
@click.option(
    "--tlscert",
    default=None,
    show_default=True,
    help="Path to TLS certificate file used for client authentication (PEM encoded)",
)
@click.option(
    "--tlskey",
    default=None,
    show_default=True,
    help="Path to TLS key file used for the '--tlscert' certificate (PEM encoded)",
)
@click.option(
    "--tlscacert",
    default=None,
    show_default=True,
    help="Trust certs signed only by this CA (PEM encoded). Implies '--tlsverify'.",
)
@click.pass_context
def cli(ctx, host, tlsverify, tlscert, tlskey, tlscacert):
    """
    Command line interface for kleened.
    """
    host = urlparse(host)
    if host.query != "" or host.params != "" or host.fragment != "":
        ctx.fail("Could not parse the '--host' parameter")

    if tlscert is not None and tlskey is None:
        ctx.fail("When '--tlscert' is set you must also provide the '--tlskey'")

    connection_config.host = host
    connection_config.tlsverify = tlsverify
    connection_config.tlscert = tlscert
    connection_config.tlskey = tlskey
    connection_config.tlscacert = tlscacert


cli.add_command(container_root, name="container")
cli.add_command(image_root, name="image")
cli.add_command(network_root, name="network")
cli.add_command(volume_root, name="volume")
cli.add_command(run, name="run")

if __name__ == "__main__":
    cli()
