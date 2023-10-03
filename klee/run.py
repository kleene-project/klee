import click

from .container import create_, start_, connect_
from .richclick import console, RichCommand
from .utils import KLEE_MSG


@click.command(
    cls=RichCommand, name="run", context_settings={"ignore_unknown_options": True}
)
@click.option("--name", default="", help="Assign a name to the container")
@click.option(
    "--user",
    "-u",
    default="",
    help="Alternate user that should be used for starting the container",
)
@click.option("--network", "-n", default=None, help="Connect a container to a network")
@click.option(
    "--ip",
    default=None,
    help="IPv4 address (e.g., 172.30.100.104). If the '--network' parameter is not set '--ip' is ignored.",
)
@click.option(
    "--volume",
    "-v",
    multiple=True,
    default=None,
    help="Bind mount a volume to the container",
)
@click.option(
    "--env",
    "-e",
    multiple=True,
    default=None,
    help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)",
)
@click.option(
    "--jailparam",
    "-J",
    multiple=True,
    default=["mount.devfs"],
    show_default=True,
    help="Specify a jail parameters, see jail(8) for details",
)
@click.option(
    "--attach", "-a", default=False, is_flag=True, help="Attach to STDOUT/STDERR"
)
@click.option(
    "--interactive",
    "-i",
    default=False,
    is_flag=True,
    help="Send terminal input to container's STDIN. Ignored if '--attach' is not used.",
)
@click.option("--tty", "-t", default=False, is_flag=True, help="Allocate a pseudo-TTY")
@click.argument("image", nargs=1)
@click.argument("command", nargs=-1)
def run(
    name,
    user,
    network,
    ip,
    volume,
    env,
    jailparam,
    attach,
    interactive,
    tty,
    image,
    command,
):
    """
    Create and start a new container.

    The IMAGE parameter syntax is: (**IMAGE_ID**|**IMAGE_NAME**[:**TAG**])[:**@SNAPSHOT**]

    See the documentation for details.
    """
    response = create_(name, user, network, ip, volume, env, jailparam, image, command)
    if response is None or response.status_code != 201:
        return

    container_id = response.parsed.id
    if network is not None:
        response = connect_(ip, network, container_id)
        if response is None or response.status_code != 204:
            console.print(KLEE_MSG.format(msg="could not start container"))
            return

    start_(attach, interactive, tty, [container_id])
