## Description
The `klee container update` command dynamically updates a container configuration.
You can use this command to modify jail behaviour by changing jail parameters,
or changing the container configuration such as default environment variables,
execution user, command or the name of the container.

Changing the container configurations, such as the default user, requires a
restart of the container for changes to take effect. However, many jail parameters
can be modified on a running container as well. If one or more jail parameters
cannot be modified and error will occur and a restart is required for the changes
to take effect.

> **Warning**
>
> Updating system jail parameters on a running container can cause unpredictable
> behaviour of the applications running in the container. Use this feature with
> care.
{: .warning }

Connecting/disconnecting a container to networks can be done using the
[`klee network` subcommands](klee_network.md).
Mounting/unmount a volume inside a container can be done using the
[`klee volume` subcommands](klee_volume.md).


> **Hint**
> It is not possible to manage ressource contrains in Kleene atm.
> However, FreeBSD does support ressource limiting jails/containers
> using `rctl(8)` which can be done manually until it is integrated
> into Kleene.
>
> See the [`rctl(8) manual pages`](https://man.freebsd.org/cgi/man.cgi?query=rctl)
> for details.

## Examples

### <a name="user-env"></a> Update user and environment variables (--user/--env)

Updating the user and environment variables of `my-container`:

```console
$ klee container update --user myuser --env VAR1=1 --env VAR2=2 my-container
ad813478a0ec
```

### <a name="jail-param"></a> Update a container's jail parameters (--jailparam)

Updating the jail parameters of the running container `my-container`:

```console
$ klee container update -J mount.devfs -J allow.raw_sockets my-container
ad813478a0ec
```

Note that not all parameters can be updated while the container is running:

```console
$ klee container update -J mount.devfs -J vnet my-container
an error ocurred while updating the container: '/usr/sbin/jail' returned non-zero exitcode 139 when attempting to modify the container ''
```

When an error occurs the container needs to be restarted for the changes
to take effect.
