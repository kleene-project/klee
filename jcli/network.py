import click

@click.group()
def root(name="network"):
    """Manage networks"""
    pass


@root.command(name="create")
@click.option('--driver', '-d', default="loopback", show_default=True, help="Which driver to use for the network. Only 'loopback' is possible atm.")
@click.option('--ifname', required=True, help="Name of the loopback interface used for the network")
@click.option('--subnet', required=True, help="Subnet in CIDR format for the network")
@click.argument("network_name", nargs=1)
def create(driver, ifname, subnet, network_name):
    """Create a new network"""
    click.echo("Running 'network CREATE' command")


@root.command(name="rm")
@click.argument("network", nargs=1)
def remove(networks):
    """Remove a network"""
    click.echo("Running 'network RM' command")
    click.echo(networks)


@root.command(name="ls")
def list(all_):
    """List networks"""
    click.echo("Running 'network LIST' command")


@root.command(name="connect")
@click.option('--attach', '-a', default=False, is_flag=True, help="Attach to STDOUT/STDERR")
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def connect(network, container):
    """Connect a container to a network"""
    click.echo("Running 'network CONNECT' command")


@root.command(name="disconnect")
@click.argument("network", required=True, nargs=1)
@click.argument("container", required=True, nargs=1)
def disconnect():
    """Disconnect a container to a network"""
    click.echo("Running 'network DISCONNECT' command")
