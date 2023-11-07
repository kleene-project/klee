## Description
The `klee container exec` command runs a new command in a running container.

The command being run with `klee container exec` is not restarted if
the container is restarted.

`COMMAND` must be an executable. A chained or a quoted command does not work.
For example, `klee container exec -a my_container sh -c "echo a && echo b"` works,
but `klee container exec -a my_container "echo a && echo b"` does not.

## Examples

### Run `docker exec` on a running container

First, start a container.

```console
$ klee run --name mycontainer -a 13.2-RELEASE /bin/sh /etc/rc
ad813478a0ec
created execution instance e9e43e57162d
ELF ldconfig path: /lib /usr/lib /usr/lib/compat
32-bit compatibility ldconfig path: /usr/lib32
/etc/rc: WARNING: $hostname is not set -- see rc.conf(5).
Updating motd:.
Creating and/or trimming log files.
Clearing /tmp (X related).
Updating /var/run/os-release done.
Starting syslogd.
/etc/rc: WARNING: failed to start syslogd
Starting sendmail_submit.
554 5.3.0 host "localhost" unknown: Protocol not supported
/etc/rc: WARNING: failed to start sendmail_submit
Starting sendmail_msp_queue.
Starting cron.

Tue Nov  7 09:24:44 UTC 2023

e9e43e57162d has exited with exit-code 0
```

This creates and starts a container named `mycontainer` and runs the init
script `/bin/sh /etc/rc`. Once the jail has been initialized, the process
exists and the jail runs in the background.

Next, execute a non-interactive command on the container.

```console
$ klee container exec -a mycontainer touch /tmp/execWorks
```

This creates a new file `/tmp/execWorks` inside the running container
`mycontainer`, and exits.

Next, execute an interactive `sh` shell on the container.

```console
$ klee container exec -ait mycontainer /bin/sh
```

This starts a new shell session in the container `mycontainer`.

### <a name="env"></a> Set environment variables for the exec process (--env, -e)

Next, set environment variables in the current bash session.

The `klee container exec` command run by default without any environment variables
set. Use the `--env` (or the `-e` shorthand) to set environment variables
for the process being started by `klee container exec`.

The example below creates a new shell session in the container `mycontainer` with
environment variables `$VAR_A` and `$VAR_B` set to "1" and "2" respectively.
These environment variables are only valid for the `sh` process started by that
`klee container exec` command, and are not available to other processes running inside
the container.

```console
$ klee exec -a -e VAR_A=1 -e VAR_B=2 mycontainer env
created execution instance 73dbb1c9ee03
VAR_B=2
VAR_A=1

73dbb1c9ee03 has exited with exit-code 0
```
