## Description
The `klee image build` command builds images from a Dockerfile and a
"context". A build's context is the set of files and directories located in
the specified `PATH`. The build process can refer to any of the files in the
context. For example, your build can use a [*COPY*](../builder.md#copy)
instruction to reference a file in the context.

Note that `PATH` refers to a location in the filesystem on the host where Kleened
is running. If you do not run `klee` on the host, it might be desirable to access
the context `PATH` using NFS, SSHFS or something similar.

By default the `klee image build` command will look for a `Dockerfile` at the root
of the build context (i.e., at `PATH`). The `-f`, `--file`, option lets you
specify the path to an alternative file to use instead.
This is useful in cases where the same set of files are used for multiple builds.
The path must be to a file within the build context.
If a relative path is specified then it is interpreted as relative to the root of
the context.

In most cases, it's best to put each Dockerfile in an empty directory. Then,
add to that directory only the files needed for building the Dockerfile.

If the Docker client loses connection to the daemon, the build is canceled.
This happens if you interrupt the Docker client with `CTRL-c` or if the Docker
client is killed for any reason.

## Examples
### Build with PATH

```console
$ docker build .

Uploading context 10240 bytes
Step 1/3 : FROM busybox
Pulling repository busybox
 ---> e9aa60c60128MB/2.284 MB (100%) endpoint: https://cdn-registry-1.docker.io/v1/
Step 2/3 : RUN ls -lh /
 ---> Running in 9c9e81692ae9
total 24
drwxr-xr-x    2 root     root        4.0K Mar 12  2013 bin
drwxr-xr-x    5 root     root        4.0K Oct 19 00:19 dev
drwxr-xr-x    2 root     root        4.0K Oct 19 00:19 etc
drwxr-xr-x    2 root     root        4.0K Nov 15 23:34 lib
lrwxrwxrwx    1 root     root           3 Mar 12  2013 lib64 -> lib
dr-xr-xr-x  116 root     root           0 Nov 15 23:34 proc
lrwxrwxrwx    1 root     root           3 Mar 12  2013 sbin -> bin
dr-xr-xr-x   13 root     root           0 Nov 15 23:34 sys
drwxr-xr-x    2 root     root        4.0K Mar 12  2013 tmp
drwxr-xr-x    2 root     root        4.0K Nov 15 23:34 usr
 ---> b35f4035db3f
Step 3/3 : CMD echo Hello world
 ---> Running in 02071fceb21b
 ---> f52f38b7823e
Successfully built f52f38b7823e
Removing intermediate container 9c9e81692ae9
Removing intermediate container 02071fceb21b
```

This example specifies that the `PATH` is `.`, and so all the files in the
local directory get `tar`d and sent to the Docker daemon. The `PATH` specifies
where to find the files for the "context" of the build on the Docker daemon.
Remember that the daemon could be running on a remote machine and that no
parsing of the Dockerfile happens at the client side (where you're running
`docker build`). That means that *all* the files at `PATH` get sent, not just
the ones listed to [*ADD*](../builder.md#add) in the Dockerfile.

The transfer of context from the local machine to the Docker daemon is what the
`docker` client means when you see the "Sending build context" message.

If you wish to keep the intermediate containers after the build is complete,
you must use `--rm=false`. This does not affect the build cache.

### <a name="tag"></a> Tag an image (-t, --tag)

```console
$ docker build -t vieux/apache:2.0 .
```

This will build like the previous example, but it will then tag the resulting
image. The repository name will be `vieux/apache` and the tag will be `2.0`.
[Read more about valid tags](tag.md).

You can apply multiple tags to an image. For example, you can apply the `latest`
tag to a newly built image and add another tag that references a specific
version.
For example, to tag an image both as `whenry/fedora-jboss:latest` and
`whenry/fedora-jboss:v2.1`, use the following:

```console
$ docker build -t whenry/fedora-jboss:latest -t whenry/fedora-jboss:v2.1 .
```

### <a name="file"></a> Specify a Dockerfile (-f, --file)

```console
$ docker build -f Dockerfile.debug .
```

This will use a file called `Dockerfile.debug` for the build instructions
instead of `Dockerfile`.

```console
$ curl example.com/remote/Dockerfile | docker build -f - .
```

The above command will use the current directory as the build context and read
a Dockerfile from stdin.

```console
$ docker build -f dockerfiles/Dockerfile.debug -t myapp_debug .
$ docker build -f dockerfiles/Dockerfile.prod  -t myapp_prod .
```

The above commands will build the current build context (as specified by the
`.`) twice, once using a debug version of a `Dockerfile` and once using a
production version.

```console
$ cd /home/me/myapp/some/dir/really/deep
$ docker build -f /home/me/myapp/dockerfiles/debug /home/me/myapp
$ docker build -f ../../../../dockerfiles/debug /home/me/myapp
```

These two `docker build` commands do the exact same thing. They both use the
contents of the `debug` file instead of looking for a `Dockerfile` and will use
`/home/me/myapp` as the root of the build context. Note that `debug` is in the
directory structure of the build context, regardless of how you refer to it on
the command line.

> **Note**
>
> `docker build` returns a `no such file or directory` error if the
> file or directory does not exist in the uploaded context. This may
> happen if there is no context, or if you specify a file that is
> elsewhere on the Host system. The context is limited to the current
> directory (and its children) for security reasons, and to ensure
> repeatable builds on remote Docker hosts. This is also the reason why
> `ADD ../file` does not work.

### <a name="build-arg"></a> Set build-time variables (--build-arg)

You can use `ENV` instructions in a Dockerfile to define variable
values. These values persist in the built image. However, often
persistence is not what you want. Users want to specify variables differently
depending on which host they build an image on.

A good example is `http_proxy` or source versions for pulling intermediate
files. The `ARG` instruction lets Dockerfile authors define values that users
can set at build-time using the  `--build-arg` flag:

```console
$ docker build --build-arg HTTP_PROXY=http://10.20.30.2:1234 --build-arg FTP_PROXY=http://40.50.60.5:4567 .
```

This flag allows you to pass the build-time variables that are
accessed like regular environment variables in the `RUN` instruction of the
Dockerfile. Also, these values don't persist in the intermediate or final images
like `ENV` values do.   You must add `--build-arg` for each build argument.

Using this flag will not alter the output you see when the `ARG` lines from the
Dockerfile are echoed during the build process.

For detailed information on using `ARG` and `ENV` instructions, see the
[Dockerfile reference](../builder.md).

You may also use the `--build-arg` flag without a value, in which case the value
from the local environment will be propagated into the Docker container being
built:

```console
$ export HTTP_PROXY=http://10.20.30.2:1234
$ docker build --build-arg HTTP_PROXY .
```

This is similar to how `docker run -e` works. Refer to the [`docker run` documentation](run.md#env)
for more information.