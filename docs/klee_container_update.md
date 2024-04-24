## Description

The `klee container update` command updates a container's configuration.
You can use this command to modify container environment behaviour by changing
jail parameters, or changing the container configuration such as default
environment variables, user running the process, or the name of the container.

Changing the container configurations, such as the default user, requires a
restart of the container for changes to take effect. However, many jail parameters
can be modified on a running container as well. If one or more jail parameters
cannot be modified and error will occur and a restart is required for the changes
to take effect.

> **Please note**
>
> Modifying jail parameters on a running container can cause unpredictable
> behaviour for the applications running in the container. Use with care.
{: .important }

Connecting/disconnecting a container to networks can be done using the
[`klee network` subcommands](/reference/klee/network/).

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
