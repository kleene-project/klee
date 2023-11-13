from urllib.parse import urlparse

import click


DEFAULT_HOST = "http:///var/run/kleened.sock"

ERROR_INVALID_CONFIG = (
    "Error! Config file {filepath} is not valid: parameter name '{parameter}' unknown"
)


def create_cli():
    # Importing in this order enable us to load the configuration files, and thus
    # the 'theme' parameter, before it is being used in the creation of commands.
    from .config import config

    # FIXME: Load environment variables here.
    config.load_config()
    # this changed the default "rich-cli"
    # config.theme = "click-cli"

    from .container import (
        root as container_root,
        container_create,
        container_remove,
        container_exec,
        container_list,
        container_start,
        container_stop,
        container_restart,
        container_run,
    )

    from .printing import root_cls
    from .image import root as image_root, image_list, image_build, image_remove
    from .network import root as network_root
    from .volume import root as volume_root
    from .shortcuts import SHORTCUTS

    shortcuts2command_obj = {
        # Format: <shortcut name>: <actual click command object>
        "build": image_build("build", hidden=True),
        "create": container_create("create", hidden=True),
        "exec": container_exec("exec", hidden=True),
        "lsc": container_list("lsc", hidden=True),
        "lsi": image_list(name="lsi", hidden=True),
        "restart": container_restart("restart", hidden=True),
        "rmc": container_remove("rmc", hidden=True),
        "rmi": image_remove("rmi", hidden=True),
        "run": container_run("run", hidden=True),
        "start": container_start("start", hidden=True),
        "stop": container_stop("stop", hidden=True),
    }

    @click.group(cls=root_cls(), name="klee")
    @click.version_option(version="0.0.1")
    @click.option(
        "--host",
        default=None,
        help="Host address and protocol to use. See the docs for details.",
    )
    @click.option(
        "--tlsverify/--no-tlsverify",
        default=True,
        help="Verify the server cert. Uses the CA bundle provided by Certifi unless the '--cacert' is set.",
    )
    @click.option(
        "--tlscert",
        default=None,
        help="Path to TLS certificate file used for client authentication (PEM encoded)",
    )
    @click.option(
        "--tlskey",
        default=None,
        help="Path to TLS key file used for the '--tlscert' certificate (PEM encoded)",
    )
    @click.option(
        "--tlscacert",
        default=None,
        help="Trust certs signed only by this CA (PEM encoded). Implies '--tlsverify'.",
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
            if getattr(config, param) is None:
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
