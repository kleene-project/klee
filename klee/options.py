import click

HELP_DETACH_FLAG = """
Do not output STDOUT/STDERR to the terminal.
If this is set, Klee will exit and return the container ID when the container has been started.
"""
HELP_INTERACTIVE_FLAG = (
    "Send terminal input to container's STDIN. If set, `--detach` will be ignored."
)
HELP_IP_FLAG = "IPv4 address used for the container. If omitted, an unused ip is allocated from the IPv4 subnet of `--network`."
HELP_IP6_FLAG = "IPv6 address used for the container. If omitted, an unused ip is allocated from the IPv6 subnet of `--network`."
HELP_NETWORK_DRIVER_FLAG = """
Network driver of the container.
Possible values are `ipnet`, `host`, `vnet`, and `disabled`.
"""


def exec_options(cmd):
    options = [
        click.Option(
            ["--detach", "-d"], default=False, is_flag=True, help=HELP_DETACH_FLAG
        ),
        click.Option(
            ["--interactive", "-i"],
            default=False,
            is_flag=True,
            help=HELP_INTERACTIVE_FLAG,
        ),
        click.Option(
            ["--tty", "-t"], default=False, is_flag=True, help="Allocate a pseudo-TTY"
        ),
    ]
    cmd.params.extend(options)
    return cmd


def container_create_options(cmd):
    options = [
        click.Option(
            ["--user", "-u"],
            metavar="text",
            default="",
            help="""
            Alternate user that should be used for starting the container.
            This parameter will be overwritten by the jail parameter `exec.jail_user` if it is set.
            """,
        ),
        click.Option(
            ["--env", "-e"],
            multiple=True,
            default=None,
            help="Set environment variables (e.g. --env FIRST=SomeValue --env SECOND=AnotherValue)",
        ),
        click.Option(
            ["--mount", "-m"],
            multiple=True,
            default=None,
            metavar="list",
            help="""
            Mount a volume/directory/file on the host filesystem into the container.
            Mounts are specfied using a `--mount <source>:<destination>[:rw|ro]` syntax.
            """,
        ),
        click.Option(
            ["--jailparam", "-J"],
            multiple=True,
            default=["mount.devfs", 'exec.stop="/bin/sh /etc/rc.shutdown jail"'],
            show_default=True,
            help="""
            Specify one or more jail parameters to use. See the `jail(8)` man-page for details.
            If you do not want `exec.clean` and `mount.devfs` enabled, you must actively disable them.
            """,
        ),
        click.Option(
            ["--driver", "-l"],
            show_default=True,
            default="host",
            help=HELP_NETWORK_DRIVER_FLAG,
        ),
        click.Option(
            ["--network", "-n"], default=None, help="Connect container to this network."
        ),
        click.Option(["--ip"], default=None, help=HELP_IP_FLAG),
        click.Option(["--ip6"], default=None, help=HELP_IP6_FLAG),
    ]
    cmd.params.extend(options)
    return cmd
