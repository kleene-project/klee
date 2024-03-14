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
Possible values: `ipnet`, `host`, `vnet`, and `disabled`. If no network and no network driver is supplied,
the network driver is set to `host`. If a network is specfied but no network driver, it is set to `ipnet`,
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
            Default user used when running commands in the container.
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
            Mounts are specfied using a `--mount SOURCE:DESTINATION[:rw|ro]` syntax.
            """,
        ),
        click.Option(
            ["--jailparam", "-J"],
            multiple=True,
            default=[],
            show_default=True,
            help="""
            Specify one or more jail parameters to use.
            If you do not want `mount.devfs`, `exec.clean`, and `exec.stop="/bin/sh /etc/rc.shutdown"` enabled, you must actively disable them.
            """,
        ),
        click.Option(
            ["--driver", "-l"],
            show_default=True,
            default=None,
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
