## Description
Creates a new network using a specific subnet and network type.
The `--type` can be either `loopback`, `bridge` or `custom` and defaults to `loopback`.

The `--subnet` or `--subnet6` option needs to be specified when creating a new network,
following the CIDR-notation, e.g., `192.168.1.1/24`.

To know more about the different network types and other
topics related to container networking, see [the container networking section](/run/network/).

## Examples

### Creating a loopback network

Creating a network is as simples as:

```console
$ klee network create --subnet=192.168.0.0/16 testnet
b5a603dcd304
```

This will create a new loopback network, with a corresponding loopback interface
that can be viewed with `ifconfig`.
If no other networks have been created with Kleene, the interface name will be `kleene0`.

### Creating a bridge network

A new loopback network can be created like this:

```console
$ klee network create --type=bridge --interface mynet --subnet=10.2.3.0/24 mynet
657e12442ff0
```

This will create a new bridge interface on the host named `mynet` for the network:

```console
$ ifconfig mynet
mynet: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
        ether 58:9c:fc:10:30:3d
        inet 10.2.3.1 netmask 0xffffff00 broadcast 10.2.3.255
        id 00:00:00:00:00:00 priority 32768 hellotime 2 fwddelay 15
        maxage 20 holdcnt 6 proto rstp maxaddr 2000 timeout 1200
        root id 00:00:00:00:00:00 priority 32768 ifcost 0 port 0
        groups: bridge
        nd6 options=9<PERFORMNUD,IFDISABLED>
```
