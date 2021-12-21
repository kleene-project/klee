import click

@click.group()
def root(name="container"):
    """Manage containers"""
    pass


@root.command(name="create")
@click.option('--name', default="", help="Assign a name to the container")
@click.option('--network', '-n', multiple=True, default=None, help="Connect a container to a network")
@click.option('--volume', '-v', multiple=True, default=None, help="Bind mount a volume to the container")
@click.option('--env', '-e', multiple=True, default=None, help="Set environment variables (e.g. --env FIRST=env --env SECOND=env)")
@click.option('--jailparam', '-J', multiple=True, default=["mount.devfs"], help="Specify a jail parameter, see jail(8) for details")
@click.argument("command", nargs=1)
@click.argument("args", nargs=-1)
def create(name, network, volume, env, jailparam, command, args):
    """Create a new container"""
    click.echo("Running 'CONTAINER CREATE' command")


@root.command(name="ls")
@click.option('--all', '-a', default=False, is_flag=True, help="Show all containers (default shows only running containers)")
def list(all_):
    """List containers"""
    click.echo("Running 'CONTAINER LIST' command")


@root.command(name="rm")
@click.argument("containers", nargs=-1)
def remove(containers):
    """Remove one or more containers"""
    click.echo("Running 'CONTAINER RM' command")
    click.echo(containers)


@root.command(name="start")
@click.option('--attach', '-a', default=False, is_flag=True, help="Attach to STDOUT/STDERR")
@click.argument("container", required=True, nargs=1)
@click.argument("containers", nargs=-1)
def start():
    """Start one or more stopped containers. Attach only if a single container is started"""
    click.echo("Running 'CONTAINER START' command")


@root.command(name="stop")
@click.argument("containers", nargs=-1)
def stop():
    """Stop one or more running containers"""
    click.echo("Running 'CONTAINER STOP' command")
