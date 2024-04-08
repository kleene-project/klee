## Description
Creates a new network using a specific subnet and networking driver.
The `--driver` accepts `host`, `vnet` and `loopback`  drivers.
If you don't specify the `--driver` option, the command automatically creates a
`loopback` network for you.

The `--subnet` option needs to be specified when creating a new network, following
the CIDR-notation, e.g., `192.168.1.1/24`. The subnet is used for auto-generating
IP-addresses when connecting containters to the network (assuming an IP is not
explicitly set).

When creating a `loopback` network it is also possible to give a custom name,
using the `--ifname` option, to the loopback interface created for the network.

For an in-depth discussion of the different types of network drivers and other
topics related to container networking, see [the container networking section](/run/network/).

## Examples

### Creating a VNET network

Creating a vnet network is as simples as:

```console
$ klee network create --driver=vnet --subnet=192.168.0.0/16 my-vnet
b5a603dcd304
```

This will create a new bridge interface for the network that can be viewed
with `ifconfig`.

### Creating a loopback network

A new loopback network can be created like this:

```console
$ klee network create --driver=loopback --ifname lo-net --subnet=10.2.3.0/24 my-lo-net
657e12442ff0
```

This will create a new loopback interface named `lo-net` for the network:

```console
$ ifconfig lo-net
lo-net: flags=8008<LOOPBACK,MULTICAST> metric 0 mtu 16384
        options=680003<RXCSUM,TXCSUM,LINKSTATE,RXCSUM_IPV6,TXCSUM_IPV6>
        groups: lo
        nd6 options=21<PERFORMNUD,AUTO_LINKLOCAL>
```
