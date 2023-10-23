## Examples
### Connect a running container to a network

```console
$ docker network connect multi-host-network container1
```

### Connect a container to a network when it starts

You can also use the `docker run --network=<network-name>` option to start a
container and immediately connect it to a network.

```console
$ docker run -itd --network=multi-host-network busybox
```

### <a name="ip"></a> Specify the IP address a container will use on a given network (--ip)

You can specify the IP address you want to be assigned to the container's interface.

```console
$ docker network connect --ip 10.10.36.122 multi-host-network container2
```

### <a name="link"></a> Use the legacy `--link` option (--link)

You can use `--link` option to link another container with a preferred alias

```console
$ docker network connect --link container1:c1 multi-host-network container2
```

### <a name="alias"></a> Create a network alias for a container (--alias)

`--alias` option can be used to resolve the container by another name in the network
being connected to.

```console
$ docker network connect --alias db --alias mysql multi-host-network container2
```

### Network implications of stopping, pausing, or restarting containers

You can pause, restart, and stop containers that are connected to a network.
A container connects to its configured networks when it runs.

If specified, the container's IP address(es) is reapplied when a stopped
container is restarted. If the IP address is no longer available, the container
fails to start. One way to guarantee that the IP address is available is
to specify an `--ip-range` when creating the network, and choose the static IP
address(es) from outside that range. This ensures that the IP address is not
given to another container while this container is not on the network.

```console
$ docker network create --subnet 172.20.0.0/16 --ip-range 172.20.240.0/20 multi-host-network
```

```console
$ docker network connect --ip 172.20.128.2 multi-host-network container2
```

To verify the container is connected, use the `docker network inspect` command.
Use `docker network disconnect` to remove a container from the network.

Once connected in network, containers can communicate using only another
container's IP address or name. For `overlay` networks or custom plugins that
support multi-host connectivity, containers connected to the same multi-host
network but launched from different Engines can also communicate in this way.

You can connect a container to one or more networks. The networks need not be
the same type. For example, you can connect a single container bridge and overlay
networks.