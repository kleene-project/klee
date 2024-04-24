## Examples
### <a name="all"></a> Show both running and stopped containers (-a, --all)

The `klee container ls` (or shorthand `klee lsc`) command only shows running containers by default.
To see all containers, use the `--all` (or `-a`) flag:

```console
$ klee container ls -a
 CONTAINER ID    NAME              IMAGE             COMMAND            CREATED         AUTORUN   STATUS    JID
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 e56a04bc2ecc    trusting_darwin   FreeBSD:testing   echo hello world   6 seconds ago     no      stopped
 2ec4bd8ad705    funny_bhaskara    FreeBSD:testing   /bin/sh /etc/rc    27 hours ago      no      running   1
```
