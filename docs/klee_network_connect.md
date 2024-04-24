## Description
This command is used to provide access for containers to one og more networks.
Once connected, the container can communicate with other containers in the same network.
For a discussion of the different types of network drivers, see
[the container networking section](/run/network/).

The network drivers are incompatible, since they represent fundamentally different approaches to
connectivity in FreeBSD. Thus, a container can only use of kind kind of network driver.

When a container connects to a network, an IP-address from the network's subnet
is allocated for the container. The IP-address is reserved for the container
until it is removed or disconnected from the network. Keep this in mind when
defining the networks subnet. If a network runs out of IP-addresses, connecting
a container will result in an error.

It is possible to pick a specific IP-address when connecting a container using
the `--ip` option. If the given address is already taken, the connection fails
with an error.

In general, it is only possible to connect running containers that uses the
`ipnet` network driver. However, both running `ipnet` and `vnet` containers
can be disconnected from a network while running.

To verify if a container is connected, and by which IP-address, use the
`klee network inspect` command. The `network_endpoints` section lists
all the networks that a container is connected to.

Use `klee network disconnect` to remove a container from the network.

## Examples
### Connect a running container to a network

```console
$ klee network connect testnet container1
```

### Connect a container to a network when it starts

You can also use the `klee run --network=<network-name>` option to start a
container and immediately connect it to a network.

```console
$ klee run --network=testnet FreeBSD-13.2-RELEASE
```

### <a name="ip"></a> Specify the IP address a container will use on a given network (--ip)

You can specify the IP address you want to be assigned to the container's interface.

```console
$ klee network connect --ip 10.10.36.122 testnet container2
```
