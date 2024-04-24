## Description

Run a new command in a running container.

A command executed with `klee container exec` is not restarted if
the container is restarted.

`COMMAND` must be an executable and a chained command needs to be quoted.
For example, `klee container exec my_container sh -c "echo a && echo b"` works,
but `klee container exec my_container "echo a && echo b"` does not.

## Examples

### Run `docker exec` on a running container

First, start a container.

```console
$ klee run --name mycontainer FreeBSD:latest /bin/sh /etc/rc
ad813478a0ec
created execution instance e9e43e57162d
ELF ldconfig path: /lib /usr/lib /usr/lib/compat
32-bit compatibility ldconfig path: /usr/lib32
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
script `/bin/sh /etc/rc`. Once the container has been initialized, the process
exists and the container runs in the background.

Next, execute a non-interactive command on the container:

```console
$ klee container exec mycontainer touch /tmp/execWorks
```

This creates a new file `/tmp/execWorks` inside the running container,
and exits.

Next, start an interactive shell in the container:

```console
$ klee container exec -it mycontainer /bin/sh
```

This starts a shell session in the container.

Next, set environment variables in a new shell session.

`klee container exec` runs with a minimal amount of environment variables
by default. Use the `--env` (or `-e`) to set additional environment variables
for the process.

Below, a new shell session in the container `mycontainer` is created with
environment variables `$VAR_A` and `$VAR_B` set to "1" and "2" respectively.
The environment variables are only valid for the process started by the
command that defined the variables.

```console
$ klee exec -e VAR_A=1 -e VAR_B=2 mycontainer env
created execution instance 84effca72ec8
VAR_B=2
VAR_A=1
SHELL=/bin/csh
HOME=/root
USER=root
BLOCKSIZE=K
MAIL=/var/mail/root
MM_CHARSET=UTF-8
LANG=C.UTF-8
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin:/root/bin
TERM=screen

84effca72ec8 has exited with exit-code 0
```
