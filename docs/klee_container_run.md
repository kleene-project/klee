## Description
The `klee container run` command first creates a container based on the
specified image, and then `starts` it using the specified command. That is,
`klee container run` is equivalent to `klee container create` followed by
`klee container start`. A stopped container can be restarted with all its
previous changes intact using `klee container start`.
Use `klee container ls -a` to view a list of all containers.

For information on connecting a container to a network, see the
["*Kleene network overview*"](/config/containers/container-networking/).

## Examples

### <a name="name"></a> Assign name and allocate pseudo-TTY (--name, -it)

```console
$ klee run --name test -ait FreeBSD-13.2-STABLE /bin/sh
839aee293db2
created execution instance 176b56a85a4a
#
root@d6c0fe130dba:/# exit
exit

executable 176b56a85a4a and its container exited with exit-code 0
$
```

This example runs a container named `test` using the `FreeBSD-13.2-STABLE:latest`
image. The `-ait` options instructs Kleene to allocate a pseudo-TTY connected to
the container's stdin; creating an interactive Bourne shell in the container.
In the example, the Bourne shell is quit by entering `exit`.

### <a name="volume"></a> Mount volume (-v, --read-only)

```console
$ klee run -v /foo/bar -ait FreeBSD-13.2-STABLE /bin/sh
# ls /foo
bar
```

When the target directory of a volume-mount doesn't exist, Kleened
will automatically create this directory in the container. The previous example
caused Kleened to create `/foo/bar` folder before starting the container.

```console
$ klee run -a -v /writeprotected:ro FreeBSD13.2-STABLE touch /writeprotected/here
50d478460a91
created execution instance badd96b047a5
touch: /writeprotected/here: Read-only file system
jail: /usr/bin/env -i touch /writeprotected/here: failed

executable badd96b047a5 and its container exited with exit-code 1
```

Volumes can be mounted read-only to control where a container writes files.
The `:ro` option must be postfixed the mountpoint to mark the mount as read only.

### <a name="env"></a> Set environment variables (-e, --env, --env-file)

You can define the variable and its value when running the container:

```console
$ klee run -a --env VAR1=value1 --env VAR2=value2 FreeBSD-13.2-STABLE env | grep VAR
VAR1=value1
VAR2=value2
```

If you need to use variables that you've exported to your local environment:

```console
export VAR1=value1
export VAR2=value2

$ klee run -a --env VAR1=$VAR1 --env VAR2=$VAR2 FreeBSD-13.2-STABLE env | grep VAR
VAR1=value1
VAR2=value2
```

### <a name="network"></a> Connect a container to a network (--network)

When you start a container use the `--network` flag to connect it to a network.

The following commands create a network named `my-net`, and adds a container
to the `my-net` network.

```console
$ klee network create --subnet 10.20.30.0/24 --driver vnet my-net
0974802b8ba1
$ klee container run --network=my-net FreeBSD-13.2-STABLE
f25a12f7c2e0
created execution instance a6172d3be00f
```

You can also choose the IP addresses for the container with the `--ip`
flag when you start the container on a user-defined network.

```console
$ klee run --network=my-net --ip=10.20.30.75 FreeBSD-13.2-STABLE
```

You can also start a container using the `host` network, meaning the container
will have full access to the networks of the host system.

```console
$ klee run --network=host FreeBSD-13.2-STABLE
```

When you run a command using, e.g., `klee run` you can only connect the container
to a single network. However, you can add a (possibly) running container to another
network using the `klee network connect` subcommand.

You can connect multiple containers to the same network. Once connected, the
containers can communicate easily using only another container's IP address.

You can disconnect a container from a network using the `docker network
disconnect` command.

### <a name="attach"></a> Attach to STDIN/STDOUT/STDERR (-a, --attach)

The `--attach` (or `-a`) flag tells `docker run` to bind to the container's
`STDOUT` and `STDERR`. This makes it possible to see the output if needed.

```console
$ klee run -a FreeBSD-13.2-STABLE echo test
422100eb65cc
created execution instance 29096db4ca54
test

executable 29096db4ca54 and its container exited with exit-code 0
```

### <a name="jailparam"></a> Specifying Jail parameters (-J, --jailparam)
FIXME
