import click

@click.group()
def root(name="volume"):
    """Manage volumes"""
    pass


@root.command()
@click.argument("volume_name", nargs=1)
def create(volume_name):
    """
    Create a new volume. If no volume name is provided jocker generates one.
    If the volume name already exists nothing happens.
    """
    click.echo("Running 'volume CREATE' command")


@root.command(name="ls")
def list(all_):
    """List volumes"""
    click.echo("Running 'volume LIST' command")


@root.command(name="rm")
@click.argument("volume", nargs=1)
@click.argument("volumes", nargs=-1)
def remove(volumes):
    """Remove one or more volumes"""
    click.echo("Running 'volume RM' command")
    click.echo(volumes)
