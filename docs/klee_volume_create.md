## Examples
Create a volume and then configure a container to use it:

```console
$ klee volume create hello
hello
$ sudo touch /zroot/kleene/volumes/hello/world
$ klee run -a -v hello:/there FreeBSD-13.2-STABLE ls /there
968414ee0599
created execution instance 7dbade0564df
world

executable 7dbade0564df and its container exited with exit-code 0
```

The mount is created inside the container's `/there` directory.

Multiple containers can use the same volume in the same time period. This is
useful if two containers need access to shared data. For example, if one
container writes and the other reads the data.
