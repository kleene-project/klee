## Description
Build images from a Dockerfile and a context.
A build's context is the set of files and directories located in `PATH`.
The build process can refer to any of the files in the
context. For example, a build can use the [*COPY*](/reference/dockerfile/#copy)
instruction to copy files and directories from the build context to the build container.

Note that `PATH` refers to a location in the filesystem on the host where the Kleened
backend is running. If you do not run `klee` on the host, remember to use host paths
for `PATH`. It might be desirable to access the context from the client machine running
Klee using NFS, SSHFS or something similar.

By default the `klee image build` command will look for a `Dockerfile` in the root
of the build context (i.e., at `PATH/Dockerfile`).
The `-f`, `--file`, option lets you specify the path to an alternative file to use
instead.
This is useful in cases where the same set of files are used for multiple builds.
The path specified with `--file` should be relative to the context `PATH`.

In most cases, it's best to put each Dockerfile in an empty directory. Then,
add to that directory only the files needed for building the Dockerfile.

### Build container configuration

Just like you can configure a normal container environment with networking,
jail-parameters and mounts you can configure the build container used for
creating images. The parameters used to configure the build container is
mostly identical to parameters used for `klee run`. A few differences to keep in
mind, however:

- `--from`: Overwrite the image in the `FROM`-instruction.
- `--user`: If it is not set, the user of the build container will be inherited
  from the parent image. `USER`-instructions overwrites this parameter.
- `--env`: `ENV`-instructions overwrite the values of this parameter.
- `--jailparam`: `USER`-instructions can be affected if the
  `exec.system_user`/`exec.jail_user`/`exec.system_jail_user` jail parameters
  have been set manually.

## Examples
### Build with PATH

```console
$ klee image build .
Started to build image with ID f7b6cc114e75
Step 1/3 : FROM FreeBSD13.2-STABLE:latest
Step 2/3 : RUN ls -lh /
total 72
-rw-r--r--   2 root  wheel   1.0K May 12  2022 .cshrc
-rw-r--r--   2 root  wheel   507B May 12  2022 .profile
-r--r--r--   1 root  wheel   6.0K May 12  2022 COPYRIGHT
drwxr-xr-x   2 root  wheel    46B May 12  2022 bin
drwxr-xr-x  14 root  wheel    65B May 12  2022 boot
dr-xr-xr-x   7 root  wheel   512B Nov  6 18:40 dev
drwxr-xr-x  28 root  wheel   104B May 12  2022 etc
drwxr-xr-x   5 root  wheel    67B May 12  2022 lib
drwxr-xr-x   3 root  wheel     5B May 12  2022 libexec
drwxr-xr-x   2 root  wheel     2B May 12  2022 media
drwxr-xr-x   2 root  wheel     2B May 12  2022 mnt
drwxr-xr-x   2 root  wheel     2B May 12  2022 net
dr-xr-xr-x   2 root  wheel     2B May 12  2022 proc
drwxr-xr-x   2 root  wheel   150B May 12  2022 rescue
drwxr-x---   2 root  wheel     7B May 12  2022 root
drwxr-xr-x   2 root  wheel   149B May 12  2022 sbin
lrwxr-xr-x   1 root  wheel    11B May 12  2022 sys -> usr/src/sys
drwxrwxrwt   2 root  wheel     2B May 12  2022 tmp
drwxr-xr-x  14 root  wheel    14B May 12  2022 usr
drwxr-xr-x  24 root  wheel    24B May 12  2022 var
--> Snapshot created: @7cb0ccbebd9d
Step 3/3 : CMD echo "Hello World"

image created
f7b6cc114e75
```

This example specifies that the `PATH` is `.`, and so Klee will resolve this to an
absolute path and send it to Kleened. The `PATH` specifies
where to find the files for the "context" of the build on Kleened.
If Klee is used on the same machine as Kleened, the resolved absolute `PATH` will
be the same for Klee and Kleened. If not, remember to specify the correct path
on the remote machine where Kleened is running.

### Tag an image (-t, --tag)

```console
$ klee image build -t nginx:1.24.0_13 .
```

This will build like the previous example and then tag the resulting
image with `nginx:1.24.0_13`.

### Specify a Dockerfile (-f, --file)

```console
$ klee image build -f Dockerfile.debug .
```

This will use a file called `Dockerfile.debug` for the build instructions
instead of `Dockerfile`.

```console
$ klee image build -f dockerfiles/Dockerfile.debug -t myapp_debug .
$ klee image build -f dockerfiles/Dockerfile.prod  -t myapp_prod .
```

The previous commands will build the current build two images:
One using a debug-friendly version of the Dockerfile (called `Dockerfile.debug`)
and one using a production version (called `Dockerile.prod`). Both Dockerfiles
are located in the `dockerfiles` directory in the context root.

### Set build-time variables (--build-arg)

You can use `ENV` instructions in a Dockerfile to define variable
values. These values persist in the built image. However, often
persistence is not what you want. Users want to specify variables differently
depending on which host they build an image on.

A good example is `HTTP_PROXY` for pulling intermediate files.
The `ARG` instruction lets Dockerfile authors define values that users
can set at build-time using the  `--build-arg` flag:

```console
$ klee image build --build-arg HTTP_PROXY=http://10.20.30.2:1234 .
```

This flag allows you to pass the build-time variables that are
accessed like regular environment variables in the `RUN` instructions of the
Dockerfile. Also, these values don't persist in the final image
like `ENV` values do. You must add `--build-arg` for each build argument.

For detailed information on using `ARG` and `ENV` instructions, see the
[Dockerfile reference](/reference/dockerfile).
