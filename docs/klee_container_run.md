## Description
The `klee container run` command first creates a container based on the
specified image, and then `starts` it using the specified command. That is,
`klee container run` is equivalent to `klee container create` followed by
`klee container start`. A stopped container can be restarted with all its
previous changes intact using `klee container start`.
Use `klee container ls -a` to view a list of all containers.

For information on connecting a container to a network, see the
["*Kleene network overview*"](/run/network/).

## Examples

### <a name="name"></a> Assign name and allocate pseudo-TTY (--name, -it)

```console
$ klee run --name test -it FreeBSD-13.2-RELEASE /bin/sh
839aee293db2
created execution instance 176b56a85a4a
#
root@d6c0fe130dba:/# exit
exit

executable 176b56a85a4a and its container exited with exit-code 0
$
```

This example runs a container named `test` using the `FreeBSD-13.2-STABLE:latest`
image. The `-it` options instructs Kleene to allocate a pseudo-TTY connected to
the container's stdin; creating an interactive Bourne shell in the container.
In the example, the Bourne shell is quit by entering `exit`.

### <a name="mount"></a> Mounting filesystems into containers (-m, --mount)

```console
$ klee run -m some_storage:/foo/bar -it FreeBSD-13.2-STABLE /bin/sh
...
# ls /foo
bar
# exit
$ klee volume ls
 VOLUME NAME    CREATED
──────────────────────────────
 some_storage   5 seconds ago
```

When the target directory of a mount doesn't exist, Kleened
will automatically create this directory in the container. This example
caused Kleened to create `/foo/bar` folder before starting the container.
Similarily, if the specified volume does not exist, Kleened will create
it for you. In this example the volume `some_storage` was just created.


```console
$ klee run -m archive:/writeprotected:ro FreeBSD13.2-STABLE touch /writeprotected/here
50d478460a91
created execution instance badd96b047a5
touch: /writeprotected/here: Read-only file system
jail: /usr/bin/env -i touch /writeprotected/here: failed

executable badd96b047a5 and its container exited with exit-code 1
```

Volumes can be mounted read-only to control where a container writes files.
The `:ro` option must be postfixed the mountpoint to mark the mount as read only.

```console
$ klee run -m /home/someuser/kleened:/kleened FreeBSD13.2-STABLE ls /kleened/lib
d8b860024e7d
created execution instance caccc94ab15f
api
core
kleened.ex

executable caccc94ab15f and its container exited with exit-code 0
```

Mounting arbitrary files or directories into a container is also possible by
specifying an absolute path on the host system instead of a volume name.

### <a name="env"></a> Set environment variables (-e, --env, --env-file)

You can define the variable and its value when running the container:

```console
$ klee run --env VAR1=value1 --env VAR2=value2 FreeBSD-13.2-STABLE env | grep VAR
VAR1=value1
VAR2=value2
```

If you need to use variables that you've exported to your local environment:

```console
export VAR1=value1
export VAR2=value2

$ klee run --env VAR1=$VAR1 --env VAR2=$VAR2 FreeBSD-13.2-STABLE env | grep VAR
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

### <a name="detach"></a> Start a container detached from process IO (-d, --detach)

The `--detach` (or `-d`) flag tells `docker run` ignore the container's
`STDIN`, `STDOUT` and `STDERR`. This makes it possible to avoid output making the
container run in the background.

```console
$ klee run -d FreeBSD-13.2-STABLE echo test
8d8d235e3489
created execution instance 3891db558a90
```

### <a name="jailparam"></a> Specifying Jail parameters (-J, --jailparam)

It is also possible to set jail-parameters when creating a container.
Using jail-parameters it is possible to imposing or remove restrictions on the container/jail
and generally modify the runtime environment in various ways.
See the [`jails(8) manual pages`](https://man.freebsd.org/cgi/man.cgi?query=jail) for details.

For instance, opening raw sockets is not permitted by default in jails, which is required
by, e.g., `ping(8)`:

```console
klee run FreeBSD-13.2-STABLE --network host /sbin/ping 1.1.1.1
56dd7945704e
created execution instance a7e01343d836
ping: ssend socket: Operation not permitted
jail: /usr/bin/env -i /sbin/ping 1.1.1.1: failed

executable a7e01343d836 and its container exited with exit-code 1
```

This can be allowed using jail-parameters:

```console
klee run FreeBSD-13.2-STABLE -J mount.devfs -J allow.raw_sockets --network host /sbin/ping 1.1.1.1
0efca150e755
created execution instance 1c0b446fac16
PING 1.1.1.1 (1.1.1.1): 56 data bytes
64 bytes from 1.1.1.1: icmp_seq=0 ttl=63 time=14.737 ms
64 bytes from 1.1.1.1: icmp_seq=1 ttl=63 time=16.880 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=63 time=17.589 ms
```

> **Note**
>
> Manually setting jail parameters overrides the default configuration, which is to
> enable `devfs(5)` (kernel's device namespace) mounts. Thus, it was explicitly enabled in the
> previous example using `-J mount.devfs`.
