import sys
import argparse
from urllib.parse import urlparse

import click


DEFAULT_HOST = "http:///var/run/kleened.sock"

ERROR_INVALID_CONFIG = (
    "Error! Config file {filepath} is not valid: parameter name '{parameter}' unknown"
)


def bootstrap_theme_and_config_args():
    parser = argparse.ArgumentParser(prog="bootstrap-config-file", add_help=False)
    parser.add_argument("--theme")
    parser.add_argument("--config")
    args, _rest = parser.parse_known_args()
    return args.config, args.theme


def create_cli():
    # Bootstrap the configuration retrieval before building klee's CLI
    from .config import config

    config.load_environment_variables()
    config_file, theme = bootstrap_theme_and_config_args()
    config.update_bootstrap_options(config_file, theme)
    config.load_config_file()

    from .container import (
        root as container_root,
        container_create,
        container_remove,
        container_inspect,
        container_exec,
        container_list,
        container_start,
        container_stop,
        container_restart,
        container_run,
    )

    from .printing import root_cls
    from .image import (
        root as image_root,
        image_list,
        image_build,
        image_remove,
        image_inspect,
    )
    from .network import (
        root as network_root,
        network_list,
        network_remove,
        network_inspect,
    )
    from .volume import root as volume_root, volume_list, volume_remove, volume_inspect
    from .shortcuts import SHORTCUTS

    shortcuts2command_obj = {
        # This is all the actual shortcuts.
        # The 'Shortcuts' help section prints a compacted list. See 'printing.py' for details.
        # Format: <shortcut name>: <actual click command object>
        "build": image_build("build", hidden=True),
        "create": container_create("create", hidden=True),
        "exec": container_exec("exec", hidden=True),
        "restart": container_restart("restart", hidden=True),
        "start": container_start("start", hidden=True),
        "stop": container_stop("stop", hidden=True),
        "run": container_run("run", hidden=True),
        "isc": container_inspect("isc", hidden=True),
        "isi": image_inspect("isi", hidden=True),
        "isn": network_inspect("isn", hidden=True),
        "isv": volume_inspect("isv", hidden=True),
        "lsc": container_list("lsc", hidden=True),
        "lsi": image_list(name="lsi", hidden=True),
        "lsn": network_list(name="lsn", hidden=True),
        "lsv": volume_list(name="lsv", hidden=True),
        "rmc": container_remove("rmc", hidden=True),
        "rmi": image_remove("rmi", hidden=True),
        "rmn": network_remove("rmn", hidden=True),
        "rmv": volume_remove("rmv", hidden=True),
    }

    @click.group(cls=root_cls(), name="klee")
    @click.version_option(version="0.0.1")
    @click.option("--config", default=None, help="Location of Klee config file.")
    @click.option(
        "--theme",
        default=None,
        help="Theme used for Klee's output. Possible values: 'fancy' or 'simple'. Default is 'fancy'.",
    )
    @click.option(
        "--host",
        default=None,
        help=f"Host address and protocol to use. See the docs for details. Default is `{DEFAULT_HOST}`.",
    )
    @click.option(
        "--tlsverify/--no-tlsverify",
        default=None,
        metavar="bool",
        help="Verify the server cert. Uses the CA bundle provided by Certifi, unless `tlscacert` is set.",
    )
    @click.option(
        "--tlscert",
        default=None,
        help="Path to TLS certificate file used for client authentication (PEM encoded)",
    )
    @click.option(
        "--tlskey",
        default=None,
        help="Path to TLS key file used for the `tlscert` certificate (PEM encoded)",
    )
    @click.option(
        "--tlscacert",
        default=None,
        help="Trust certs signed only by this CA (PEM encoded). Implies `tlsverify`.",
    )
    @click.pass_context
    def cli(ctx, **kwargs):
        """
        CLI to interact with Kleened.
        """
        if config.invalid_file:
            msg = ERROR_INVALID_CONFIG.format(
                filepath=config.config_filepath, parameter=config.invalid_param
            )
            click.echo(msg)
            ctx.exit(-1)

        if kwargs["host"] is None and config.host is None:
            config.host = DEFAULT_HOST

        parameters_to_merge = ["host", "tlsverify", "tlscacert", "tlscert", "tlskey"]
        for param in parameters_to_merge:
            if kwargs[param] is not None:
                setattr(config, param, kwargs[param])

        config.host = urlparse(config.host)

    cli.add_command(container_root, name="container")
    cli.add_command(image_root, name="image")
    cli.add_command(network_root, name="network")
    cli.add_command(volume_root, name="volume")

    for name in SHORTCUTS.keys():
        shortcut = shortcuts2command_obj[name]
        cli.add_command(shortcut)

    return cli
