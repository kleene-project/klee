## Examples
```console
$ klee container ls -a
 CONTAINER ID    NAME                  IMAGE          TAG      COMMAND                         CREATED              STATUS
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 f25a12f7c2e0    elegant_lumiere       cecc28cf8ad4   latest   /bin/sh /etc/rc                 About an hour ago    stopped
 0144f73be1ee    inspiring_blackwell   cecc28cf8ad4   latest   /bin/sh                         About an hour ago    stopped
 effdf5d44a5e    frosty_dubinsky       cecc28cf8ad4   latest   /bin/sh                         About an hour ago    stopped
 839aee293db2    test                  cecc28cf8ad4   latest   /bin/sh                         About an hour ago    stopped

$ klee container rm f25a effdf5d44a5e inspiring_blackwell testting
f25a12f7c2e0
effdf5d44a5e
0144f73be1ee
839aee293db2
```
