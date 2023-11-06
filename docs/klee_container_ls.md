## Examples
### <a name="all"></a> Show both running and stopped containers (-a, --all)

The `klee container ls` (or shorthand `klee lsc`) command only shows running containers by default.
To see all containers, use the `--all` (or `-a`) flag:

```console
$ klee container ls -a
 CONTAINER ID    NAME          IMAGE          TAG      COMMAND                         CREATED          STATUS
────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 5f8e437e5c95    storage       cecc28cf8ad4   latest   /bin/sh /etc/rc                 10 minutes ago   stopped
 6e33dbacde70    mycontainer   707f754571dd   latest   /bin/sh -c echo "Hello World"   14 minutes ago   stopped
```
