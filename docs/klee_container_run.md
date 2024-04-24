## Description
Create a container based on the specified image, and then start it using
the specified command. `klee container run` is equivalent to `klee container create`
followed by `klee container start`.

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
In this example, the user quits the shell by typing `exit`.

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
will automatically creates it in the container. This example
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

The following commands create a network named `testnet`, and adds a container
to it.

```console
$ klee network create --subnet 10.20.30.0/24 --type loopback testnet
dcd762b8f34c
$ klee container run --network testnet FreeBSD
59e291c07673
created execution instance 4b4998af008a
... container initialization output ...
4b4998af008a has exited with exit-code 0
```

You can also choose the IP addresses for the container with the `--ip`
options, when you start the container on a user-defined network.

```console
$ klee run --network=testnet --ip=10.20.30.75 FreeBSD:testing
```

You can also create a container with full access to the host networking using the `host` network-driver.

```console
$ klee run --driver=host FreeBSD:latest
```

When you create a container using, e.g., `klee run` you can only connect the container
to a single network. However, you can add containers to additional
networks using `klee network connect`.

Containers can be disconnected from networks using `klee network disconnect`.

### <a name="detach"></a> Start a container detached from process IO (-d, --detach)

The `--detach` (or `-d`) flag tells `klee run` to ignore output from the container's
`STDIN`, `STDOUT` and `STDERR`.

```console
$ klee run -d FreeBSD-13.2-STABLE echo test
8d8d235e3489
created execution instance 3891db558a90
```

Once the container has started, Klee exists and the container runs in the background.

### <a name="jailparam"></a> Specifying Jail parameters (-J, --jailparam)

It is possible to set jail-parameters when creating a container.
Using jail-parameters it is possible to configure the container/jail environment
in various ways. See the [`jails(8)` manual pages](https://man.freebsd.org/cgi/man.cgi?query=jail)
for details on the available jail-parameters and the Kleene handbook section on
[jail parameters](/run/jail-parameters/) for a discussion on how jail parameters
is used by Kleene.

For example, opening raw sockets is not permitted in containers by default,
which is required by, e.g., `ping(8)`:

```console
$ klee run FreeBSD /sbin/ping 1.1.1.1
56dd7945704e
created execution instance a7e01343d836
ping: ssend socket: Operation not permitted
jail: /usr/bin/env -i /sbin/ping 1.1.1.1: failed

executable a7e01343d836 and its container exited with exit-code 1
```

This can be allowed using jail-parameters:

```console
klee run -J allow.raw_sockets FreeBSD /sbin/ping 1.1.1.1
0efca150e755
created execution instance 1c0b446fac16
PING 1.1.1.1 (1.1.1.1): 56 data bytes
64 bytes from 1.1.1.1: icmp_seq=0 ttl=63 time=14.737 ms
64 bytes from 1.1.1.1: icmp_seq=1 ttl=63 time=16.880 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=63 time=17.589 ms
```

> **Note**
>
> Manually setting jail parameters can potentially overwrite Kleene's own configurations
> which, for instance, is used to configure container networking. Tailoring container
> environments with jail parameters is a powerful feature of Kleene, but use it with caution.
