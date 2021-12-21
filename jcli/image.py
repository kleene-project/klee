import click

@click.group()
def root(name="image"):
    """Manage images"""
    pass


@root.command()
@click.option('--file', '-f', default="Dockerfile", help="Name of the Dockerfile (default: 'Dockerfile')")
@click.option('--tag', '-t', default="", help="Name and optionally a tag in the 'name:tag' format")
@click.option('--quiet', '-q', multiple=True, default=None, help="Suppress the build output and print image ID on success (default: false)")
@click.argument("path", nargs=1)
def build(file_, tag, quiet, path):
    """Build an image from a context + Dockerfile located in PATH"""
    click.echo("Running 'image CREATE' command")


@root.command(name="ls")
@click.option('--all', '-a', default=False, is_flag=True, help="Show all images (default shows only running images)")
def list(all_):
    """List images"""
    click.echo("Running 'image LIST' command")


@root.command(name="rm")
@click.argument("images", nargs=-1)
def remove(images):
    """Remove one or more images"""
    click.echo("Running 'image RM' command")
    click.echo(images)
