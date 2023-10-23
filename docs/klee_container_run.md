## Description
The `docker run` command first `creates` a writeable container layer over the
specified image, and then `starts` it using the specified command. That is,
`docker run` is equivalent to the API `/containers/create` then
`/containers/(id)/start`. A stopped container can be restarted with all its
previous changes intact using `docker start`. See `docker ps -a` to view a list
of all containers.

For information on connecting a container to a network, see the ["*Docker network overview*"](https://docs.docker.com/network/).

## Examples
### <a name="name"></a> Assign name and allocate pseudo-TTY (--name, -it)

```console
$ docker run --name test -it debian

root@d6c0fe130dba:/# exit 13
$ echo $?
13
$ docker ps -a | grep test
d6c0fe130dba        debian:7            "/bin/bash"         26 seconds ago      Exited (13) 17 seconds ago                         test
```

This example runs a container named `test` using the `debian:latest`
image. The `-it` instructs Docker to allocate a pseudo-TTY connected to
the container's stdin; creating an interactive `bash` shell in the container.
In the example, the `bash` shell is quit by entering
`exit 13`. This exit code is passed on to the caller of
`docker run`, and is recorded in the `test` container's metadata.

### <a name="cidfile"></a> Capture container ID (--cidfile)

```console
$ docker run --cidfile /tmp/docker_test.cid ubuntu echo "test"
```

This will create a container and print `test` to the console. The `cidfile`
flag makes Docker attempt to create a new file and write the container ID to it.
If the file exists already, Docker will return an error. Docker will close this
file when `docker run` exits.

### <a name="privileged"></a> Full container capabilities (--privileged)

```console
$ docker run -t -i --rm ubuntu bash
root@bc338942ef20:/# mount -t tmpfs none /mnt
mount: permission denied
```

This will *not* work, because by default, most potentially dangerous kernel
capabilities are dropped; including `cap_sys_admin` (which is required to mount
filesystems). However, the `--privileged` flag will allow it to run:

```console
$ docker run -t -i --privileged ubuntu bash
root@50e3f57e16e6:/# mount -t tmpfs none /mnt
root@50e3f57e16e6:/# df -h
Filesystem      Size  Used Avail Use% Mounted on
none            1.9G     0  1.9G   0% /mnt
```

The `--privileged` flag gives *all* capabilities to the container, and it also
lifts all the limitations enforced by the `device` cgroup controller. In other
words, the container can then do almost everything that the host can do. This
flag exists to allow special use-cases, like running Docker within Docker.

### <a name="workdir"></a> Set working directory (-w, --workdir)

```console
$ docker  run -w /path/to/dir/ -i -t  ubuntu pwd
```

The `-w` lets the command being executed inside directory given, here
`/path/to/dir/`. If the path does not exist it is created inside the container.

### <a name="storage-opt"></a> Set storage driver options per container (--storage-opt)

```console
$ docker run -it --storage-opt size=120G fedora /bin/bash
```

This (size) will allow to set the container filesystem size to 120G at creation time.
This option is only available for the `devicemapper`, `btrfs`, `overlay2`,
`windowsfilter` and `zfs` graph drivers.
For the `devicemapper`, `btrfs`, `windowsfilter` and `zfs` graph drivers,
user cannot pass a size less than the Default BaseFS Size.
For the `overlay2` storage driver, the size option is only available if the
backing filesystem is `xfs` and mounted with the `pquota` mount option.
Under these conditions, user can pass any size less than the backing filesystem size.

### <a name="tmpfs"></a> Mount tmpfs (--tmpfs)

```console
$ docker run -d --tmpfs /run:rw,noexec,nosuid,size=65536k my_image
```

The `--tmpfs` flag mounts an empty tmpfs into the container with the `rw`,
`noexec`, `nosuid`, `size=65536k` options.

### <a name="volume"></a> Mount volume (-v, --read-only)

```console
$ docker  run  -v `pwd`:`pwd` -w `pwd` -i -t  ubuntu pwd
```

The `-v` flag mounts the current working directory into the container. The `-w`
lets the command being executed inside the current working directory, by
changing into the directory to the value returned by `pwd`. So this
combination executes the command using the container, but inside the
current working directory.

```console
$ docker run -v /doesnt/exist:/foo -w /foo -i -t ubuntu bash
```

When the host directory of a bind-mounted volume doesn't exist, Docker
will automatically create this directory on the host for you. In the
example above, Docker will create the `/doesnt/exist`
folder before starting your container.

```console
$ docker run --read-only -v /icanwrite busybox touch /icanwrite/here
```

Volumes can be used in combination with `--read-only` to control where
a container writes files. The `--read-only` flag mounts the container's root
filesystem as read only prohibiting writes to locations other than the
specified volumes for the container.

```console
$ docker run -t -i -v /var/run/docker.sock:/var/run/docker.sock -v /path/to/static-docker-binary:/usr/bin/docker busybox sh
```

By bind-mounting the Docker Unix socket and statically linked Docker
binary (refer to [get the Linux binary](https://docs.docker.com/engine/install/binaries/#install-static-binaries)),
you give the container the full access to create and manipulate the host's
Docker daemon.

On Windows, the paths must be specified using Windows-style semantics.

```powershell
PS C:\> docker run -v c:\foo:c:\dest microsoft/nanoserver cmd /s /c type c:\dest\somefile.txt
Contents of file

PS C:\> docker run -v c:\foo:d: microsoft/nanoserver cmd /s /c type d:\somefile.txt
Contents of file
```

The following examples will fail when using Windows-based containers, as the
destination of a volume or bind mount inside the container must be one of:
a non-existing or empty directory; or a drive other than C:. Further, the source
of a bind mount must be a local directory, not a file.

```powershell
net use z: \\remotemachine\share
docker run -v z:\foo:c:\dest ...
docker run -v \\uncpath\to\directory:c:\dest ...
docker run -v c:\foo\somefile.txt:c:\dest ...
docker run -v c:\foo:c: ...
docker run -v c:\foo:c:\existing-directory-with-contents ...
```

For in-depth information about volumes, refer to [manage data in containers](https://docs.docker.com/storage/volumes/)


### <a name="mount"></a> Add bind mounts or volumes using the --mount flag

The `--mount` flag allows you to mount volumes, host-directories and `tmpfs`
mounts in a container.

The `--mount` flag supports most options that are supported by the `-v` or the
`--volume` flag, but uses a different syntax. For in-depth information on the
`--mount` flag, and a comparison between `--volume` and `--mount`, refer to
[Bind mounts](https://docs.docker.com/storage/bind-mounts/).

Even though there is no plan to deprecate `--volume`, usage of `--mount` is recommended.

Examples:

```console
$ docker run --read-only --mount type=volume,target=/icanwrite busybox touch /icanwrite/here
```

```console
$ docker run -t -i --mount type=bind,src=/data,dst=/data busybox sh
```

### <a name="publish"></a> Publish or expose port (-p, --expose)

```console
$ docker run -p 127.0.0.1:80:8080/tcp ubuntu bash
```

This binds port `8080` of the container to TCP port `80` on `127.0.0.1` of the host
machine. You can also specify `udp` and `sctp` ports.
The [Docker User Guide](https://docs.docker.com/network/links/)
explains in detail how to manipulate ports in Docker.

Note that ports which are not bound to the host (i.e., `-p 80:80` instead of
`-p 127.0.0.1:80:80`) will be accessible from the outside. This also applies if
you configured UFW to block this specific port, as Docker manages its
own iptables rules. [Read more](https://docs.docker.com/network/iptables/)

```console
$ docker run --expose 80 ubuntu bash
```

This exposes port `80` of the container without publishing the port to the host
system's interfaces.

### <a name="pull"></a> Set the pull policy (--pull)

Use the `--pull` flag to set the image pull policy when creating (and running)
the container.

The `--pull` flag can take one of these values:

| Value               | Description                                                                                                       |
|:--------------------|:------------------------------------------------------------------------------------------------------------------|
| `missing` (default) | Pull the image if it was not found in the image cache, or use the cached image otherwise.                         |
| `never`             | Do not pull the image, even if it's missing, and produce an error if the image does not exist in the image cache. |
| `always`            | Always perform a pull before creating the container.                                                              |

When creating (and running) a container from an image, the daemon checks if the
image exists in the local image cache. If the image is missing, an error is
returned to the CLI, allowing it to initiate a pull.

The default (`missing`) is to only pull the image if it is not present in the
daemon's image cache. This default allows you to run images that only exist
locally (for example, images you built from a Dockerfile, but that have not
been pushed to a registry), and reduces networking.

The `always` option always initiates a pull before creating the container. This
option makes sure the image is up-to-date, and prevents you from using outdated
images, but may not be suitable in situations where you want to test a locally
built image before pushing (as pulling the image overwrites the existing image
in the image cache).

The `never` option disables (implicit) pulling images when creating containers,
and only uses images that are available in the image cache. If the specified
image is not found, an error is produced, and the container is not created.
This option is useful in situations where networking is not available, or to
prevent images from being pulled implicitly when creating containers.

The following example shows `docker run` with the `--pull=never` option set,
which produces en error as the image is missing in the image-cache:

```console
$ docker run --pull=never hello-world
docker: Error response from daemon: No such image: hello-world:latest.
```

### <a name="env"></a> Set environment variables (-e, --env, --env-file)

```console
$ docker run -e MYVAR1 --env MYVAR2=foo --env-file ./env.list ubuntu bash
```

Use the `-e`, `--env`, and `--env-file` flags to set simple (non-array)
environment variables in the container you're running, or overwrite variables
that are defined in the Dockerfile of the image you're running.

You can define the variable and its value when running the container:

```console
$ docker run --env VAR1=value1 --env VAR2=value2 ubuntu env | grep VAR
VAR1=value1
VAR2=value2
```

You can also use variables that you've exported to your local environment:

```console
export VAR1=value1
export VAR2=value2

$ docker run --env VAR1 --env VAR2 ubuntu env | grep VAR
VAR1=value1
VAR2=value2
```

When running the command, the Docker CLI client checks the value the variable
has in your local environment and passes it to the container.
If no `=` is provided and that variable is not exported in your local
environment, the variable won't be set in the container.

You can also load the environment variables from a file. This file should use
the syntax `<variable>=value` (which sets the variable to the given value) or
`<variable>` (which takes the value from the local environment), and `#` for comments.

```console
$ cat env.list
# This is a comment
VAR1=value1
VAR2=value2
USER

$ docker run --env-file env.list ubuntu env | grep -E 'VAR|USER'
VAR1=value1
VAR2=value2
USER=jonzeolla
```

### <a name="label"></a> Set metadata on container (-l, --label, --label-file)

A label is a `key=value` pair that applies metadata to a container. To label a container with two labels:

```console
$ docker run -l my-label --label com.example.foo=bar ubuntu bash
```

The `my-label` key doesn't specify a value so the label defaults to an empty
string (`""`). To add multiple labels, repeat the label flag (`-l` or `--label`).

The `key=value` must be unique to avoid overwriting the label value. If you
specify labels with identical keys but different values, each subsequent value
overwrites the previous. Docker uses the last `key=value` you supply.

Use the `--label-file` flag to load multiple labels from a file. Delimit each
label in the file with an EOL mark. The example below loads labels from a
labels file in the current directory:

```console
$ docker run --label-file ./labels ubuntu bash
```

The label-file format is similar to the format for loading environment
variables. (Unlike environment variables, labels are not visible to processes
running inside a container.) The following example illustrates a label-file
format:

```console
com.example.label1="a label"

# this is a comment
com.example.label2=another\ label
com.example.label3
```

You can load multiple label-files by supplying multiple  `--label-file` flags.

For additional information on working with labels, see [*Labels - custom
metadata in Docker*](https://docs.docker.com/config/labels-custom-metadata/) in
the Docker User Guide.

### <a name="network"></a> Connect a container to a network (--network)

When you start a container use the `--network` flag to connect it to a network.
The following commands create a network named `my-net`, and adds a `busybox` container
to the `my-net` network.

```console
$ docker network create my-net
$ docker run -itd --network=my-net busybox
```

You can also choose the IP addresses for the container with `--ip` and `--ip6`
flags when you start the container on a user-defined network.

```console
$ docker run -itd --network=my-net --ip=10.10.9.75 busybox
```

If you want to add a running container to a network use the `docker network connect` subcommand.

You can connect multiple containers to the same network. Once connected, the
containers can communicate easily using only another container's IP address
or name. For `overlay` networks or custom plugins that support multi-host
connectivity, containers connected to the same multi-host network but launched
from different Engines can also communicate in this way.

> **Note**
>
> The default bridge network only allow containers to communicate with each other using
> internal IP addresses. User-created bridge networks provide DNS resolution between
> containers using container names.

You can disconnect a container from a network using the `docker network
disconnect` command.

### <a name="volumes-from"></a> Mount volumes from container (--volumes-from)

```console
$ docker run --volumes-from 777f7dc92da7 --volumes-from ba8c0c54f0f2:ro -i -t ubuntu pwd
```

The `--volumes-from` flag mounts all the defined volumes from the referenced
containers. Containers can be specified by repetitions of the `--volumes-from`
argument. The container ID may be optionally suffixed with `:ro` or `:rw` to
mount the volumes in read-only or read-write mode, respectively. By default,
the volumes are mounted in the same mode (read write or read only) as
the reference container.

Labeling systems like SELinux require that proper labels are placed on volume
content mounted into a container. Without a label, the security system might
prevent the processes running inside the container from using the content. By
default, Docker does not change the labels set by the OS.

To change the label in the container context, you can add either of two suffixes
`:z` or `:Z` to the volume mount. These suffixes tell Docker to relabel file
objects on the shared volumes. The `z` option tells Docker that two containers
share the volume content. As a result, Docker labels the content with a shared
content label. Shared volume labels allow all containers to read/write content.
The `Z` option tells Docker to label the content with a private unshared label.
Only the current container can use a private volume.

### <a name="attach"></a> Attach to STDIN/STDOUT/STDERR (-a, --attach)

The `--attach` (or `-a`) flag tells `docker run` to bind to the container's
`STDIN`, `STDOUT` or `STDERR`. This makes it possible to manipulate the output
and input as needed.

```console
$ echo "test" | docker run -i -a stdin ubuntu cat -
```

This pipes data into a container and prints the container's ID by attaching
only to the container's `STDIN`.

```console
$ docker run -a stderr ubuntu echo test
```

This isn't going to print anything unless there's an error because we've
only attached to the `STDERR` of the container. The container's logs
still store what's been written to `STDERR` and `STDOUT`.

```console
$ cat somefile | docker run -i -a stdin mybuilder dobuild
```

This is a way of using `--attach` to pipe a build file into a container.
The container's ID will be printed after the build is done and the build
logs could be retrieved using `docker logs`. This is
useful if you need to pipe a file or something else into a container and
retrieve the container's ID once the container has finished running.

See also [the `docker cp` command](cp.md).

### <a name="device"></a> Add host device to container (--device)

```console
$ docker run -it --rm \
    --device=/dev/sdc:/dev/xvdc \
    --device=/dev/sdd \
    --device=/dev/zero:/dev/foobar \
    ubuntu ls -l /dev/{xvdc,sdd,foobar}

brw-rw---- 1 root disk 8, 2 Feb  9 16:05 /dev/xvdc
brw-rw---- 1 root disk 8, 3 Feb  9 16:05 /dev/sdd
crw-rw-rw- 1 root root 1, 5 Feb  9 16:05 /dev/foobar
```

It is often necessary to directly expose devices to a container. The `--device`
option enables that. For example, a specific block storage device or loop
device or audio device can be added to an otherwise unprivileged container
(without the `--privileged` flag) and have the application directly access it.

By default, the container will be able to `read`, `write` and `mknod` these devices.
This can be overridden using a third `:rwm` set of options to each `--device`
flag. If the container is running in privileged mode, then the permissions specified
will be ignored.

```console
$ docker run --device=/dev/sda:/dev/xvdc --rm -it ubuntu fdisk  /dev/xvdc

Command (m for help): q
$ docker run --device=/dev/sda:/dev/xvdc:r --rm -it ubuntu fdisk  /dev/xvdc
You will not be able to write the partition table.

Command (m for help): q

$ docker run --device=/dev/sda:/dev/xvdc:rw --rm -it ubuntu fdisk  /dev/xvdc

Command (m for help): q

$ docker run --device=/dev/sda:/dev/xvdc:m --rm -it ubuntu fdisk  /dev/xvdc
fdisk: unable to open /dev/xvdc: Operation not permitted
```

> **Note**
>
> The `--device` option cannot be safely used with ephemeral devices. Block devices
> that may be removed should not be added to untrusted containers with `--device`.

For Windows, the format of the string passed to the `--device` option is in
the form of `--device=<IdType>/<Id>`. Beginning with Windows Server 2019
and Windows 10 October 2018 Update, Windows only supports an IdType of
`class` and the Id as a [device interface class
GUID](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/overview-of-device-interface-classes).
Refer to the table defined in the [Windows container
docs](https://docs.microsoft.com/en-us/virtualization/windowscontainers/deploy-containers/hardware-devices-in-containers)
for a list of container-supported device interface class GUIDs.

If this option is specified for a process-isolated Windows container, _all_
devices that implement the requested device interface class GUID are made
available in the container. For example, the command below makes all COM
ports on the host visible in the container.

```powershell
PS C:\> docker run --device=class/86E0D1E0-8089-11D0-9CE4-08003E301F73 mcr.microsoft.com/windows/servercore:ltsc2019
```

> **Note**
>
> The `--device` option is only supported on process-isolated Windows containers.
> This option fails if the container isolation is `hyperv` or when running Linux
> Containers on Windows (LCOW).

### <a name="device-cgroup-rule"></a> Using dynamically created devices (--device-cgroup-rule)

Devices available to a container are assigned at creation time. The
assigned devices will both be added to the cgroup.allow file and
created into the container once it is run. This poses a problem when
a new device needs to be added to running container.

One of the solutions is to add a more permissive rule to a container
allowing it access to a wider range of devices. For example, supposing
our container needs access to a character device with major `42` and
any number of minor number (added as new devices appear), the
following rule would be added:

```console
$ docker run -d --device-cgroup-rule='c 42:* rmw' -name my-container my-image
```

Then, a user could ask `udev` to execute a script that would `docker exec my-container mknod newDevX c 42 <minor>`
the required device when it is added.

> **Note**: initially present devices still need to be explicitly added to the
> `docker run` / `docker create` command.

### <a name="gpus"></a> Access an NVIDIA GPU

The `--gpus` flag allows you to access NVIDIA GPU resources. First you need to
install [nvidia-container-runtime](https://nvidia.github.io/nvidia-container-runtime/).
Visit [Specify a container's resources](https://docs.docker.com/config/containers/resource_constraints/)
for more information.

To use `--gpus`, specify which GPUs (or all) to use. If no value is provided, all
available GPUs are used. The example below exposes all available GPUs.

```console
$ docker run -it --rm --gpus all ubuntu nvidia-smi
```

Use the `device` option to specify GPUs. The example below exposes a specific
GPU.

```console
$ docker run -it --rm --gpus device=GPU-3a23c669-1f69-c64e-cf85-44e9b07e7a2a ubuntu nvidia-smi
```

The example below exposes the first and third GPUs.

```console
$ docker run -it --rm --gpus '"device=0,2"' nvidia-smi
```

### <a name="restart"></a> Restart policies (--restart)

Use Docker's `--restart` to specify a container's *restart policy*. A restart
policy controls whether the Docker daemon restarts a container after exit.
Docker supports the following restart policies:

| Policy                     | Result                                                                                                                                                                                                                                                           |
|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `no`                       | Do not automatically restart the container when it exits. This is the default.                                                                                                                                                                                   |
| `on-failure[:max-retries]` | Restart only if the container exits with a non-zero exit status. Optionally, limit the number of restart retries the Docker daemon attempts.                                                                                                                     |
| `unless-stopped`           | Restart the container unless it is explicitly stopped or Docker itself is stopped or restarted.                                                                                                                                                                  |
| `always`                   | Always restart the container regardless of the exit status. When you specify always, the Docker daemon will try to restart the container indefinitely. The container will also always start on daemon startup, regardless of the current state of the container. |

```console
$ docker run --restart=always redis
```

This will run the `redis` container with a restart policy of **always**
so that if the container exits, Docker will restart it.

More detailed information on restart policies can be found in the
[Restart Policies (--restart)](../run.md#restart-policies---restart)
section of the Docker run reference page.

### <a name="add-host"></a> Add entries to container hosts file (--add-host)

You can add other hosts into a container's `/etc/hosts` file by using one or
more `--add-host` flags. This example adds a static address for a host named
`docker`:

```console
$ docker run --add-host=docker:93.184.216.34 --rm -it alpine

/ # ping docker
PING docker (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: seq=0 ttl=37 time=93.052 ms
64 bytes from 93.184.216.34: seq=1 ttl=37 time=92.467 ms
64 bytes from 93.184.216.34: seq=2 ttl=37 time=92.252 ms
^C
--- docker ping statistics ---
4 packets transmitted, 4 packets received, 0% packet loss
round-trip min/avg/max = 92.209/92.495/93.052 ms
```

Sometimes you need to connect to the Docker host from within your
container. To enable this, pass the Docker host's IP address to
the container using the `--add-host` flag. To find the host's address,
use the `ip addr show` command.

The flags you pass to `ip addr show` depend on whether you are
using IPv4 or IPv6 networking in your containers. Use the following
flags for IPv4 address retrieval for a network device named `eth0`:

```console
$ HOSTIP=`ip -4 addr show scope global dev eth0 | grep inet | awk '{print $2}' | cut -d / -f 1 | sed -n 1p`
$ docker run  --add-host=docker:${HOSTIP} --rm -it debian
```

For IPv6 use the `-6` flag instead of the `-4` flag. For other network
devices, replace `eth0` with the correct device name (for example `docker0`
for the bridge device).

### <a name="ulimit"></a> Set ulimits in container (--ulimit)

Since setting `ulimit` settings in a container requires extra privileges not
available in the default container, you can set these using the `--ulimit` flag.
`--ulimit` is specified with a soft and hard limit as such:
`<type>=<soft limit>[:<hard limit>]`, for example:

```console
$ docker run --ulimit nofile=1024:1024 --rm debian sh -c "ulimit -n"
1024
```

> **Note**
>
> If you do not provide a `hard limit`, the `soft limit` is used
> for both values. If no `ulimits` are set, they are inherited from
> the default `ulimits` set on the daemon. The `as` option is disabled now.
> In other words, the following script is not supported:
>
> ```console
> $ docker run -it --ulimit as=1024 fedora /bin/bash
> ```

The values are sent to the appropriate `syscall` as they are set.
Docker doesn't perform any byte conversion. Take this into account when setting the values.

#### For `nproc` usage

Be careful setting `nproc` with the `ulimit` flag as `nproc` is designed by Linux to set the
maximum number of processes available to a user, not to a container. For example, start four
containers with `daemon` user:

```console
$ docker run -d -u daemon --ulimit nproc=3 busybox top

$ docker run -d -u daemon --ulimit nproc=3 busybox top

$ docker run -d -u daemon --ulimit nproc=3 busybox top

$ docker run -d -u daemon --ulimit nproc=3 busybox top
```

The 4th container fails and reports "[8] System error: resource temporarily unavailable" error.
This fails because the caller set `nproc=3` resulting in the first three containers using up
the three processes quota set for the `daemon` user.

### <a name="stop-signal"></a> Stop container with signal (--stop-signal)

The `--stop-signal` flag sets the system call signal that will be sent to the
container to exit. This signal can be a signal name in the format `SIG<NAME>`,
for instance `SIGKILL`, or an unsigned number that matches a position in the
kernel's syscall table, for instance `9`.

The default is `SIGTERM` if not specified.

### <a name="security-opt"></a> Optional security options (--security-opt)

On Windows, this flag can be used to specify the `credentialspec` option.
The `credentialspec` must be in the format `file://spec.txt` or `registry://keyname`.

### <a name="stop-timeout"></a> Stop container with timeout (--stop-timeout)

The `--stop-timeout` flag sets the number of seconds to wait for the container
to stop after sending the pre-defined (see `--stop-signal`) system call signal.
If the container does not exit after the timeout elapses, it is forcibly killed
with a `SIGKILL` signal.

If `--stop-timeout` is set to `-1`, no timeout is applied, and the daemon will
wait indefinitely for the container to exit.

The default is determined by the daemon, and is 10 seconds for Linux containers,
and 30 seconds for Windows containers.

### <a name="isolation"></a> Specify isolation technology for container (--isolation)

This option is useful in situations where you are running Docker containers on
Windows. The `--isolation=<value>` option sets a container's isolation technology.
On Linux, the only supported is the `default` option which uses Linux namespaces.
These two commands are equivalent on Linux:

```console
$ docker run -d busybox top
$ docker run -d --isolation default busybox top
```

On Windows, `--isolation` can take one of these values:

| Value     | Description                                                                                |
|:----------|:-------------------------------------------------------------------------------------------|
| `default` | Use the value specified by the Docker daemon's `--exec-opt` or system default (see below). |
| `process` | Shared-kernel namespace isolation.                                                         |
| `hyperv`  | Hyper-V hypervisor partition-based isolation.                                              |

The default isolation on Windows server operating systems is `process`, and `hyperv`
on Windows client operating systems, such as Windows 10. Process isolation has better
performance, but requires that the image and host use the same kernel version.

On Windows server, assuming the default configuration, these commands are equivalent
and result in `process` isolation:

```powershell
PS C:\> docker run -d microsoft/nanoserver powershell echo process
PS C:\> docker run -d --isolation default microsoft/nanoserver powershell echo process
PS C:\> docker run -d --isolation process microsoft/nanoserver powershell echo process
```

If you have set the `--exec-opt isolation=hyperv` option on the Docker `daemon`, or
are running against a Windows client-based daemon, these commands are equivalent and
result in `hyperv` isolation:

```powershell
PS C:\> docker run -d microsoft/nanoserver powershell echo hyperv
PS C:\> docker run -d --isolation default microsoft/nanoserver powershell echo hyperv
PS C:\> docker run -d --isolation hyperv microsoft/nanoserver powershell echo hyperv
```

### <a name="memory"></a> Specify hard limits on memory available to containers (-m, --memory)

These parameters always set an upper limit on the memory available to the container. On Linux, this
is set on the cgroup and applications in a container can query it at `/sys/fs/cgroup/memory/memory.limit_in_bytes`.

On Windows, this will affect containers differently depending on what type of isolation is used.

- With `process` isolation, Windows will report the full memory of the host system, not the limit to applications running inside the container

    ```powershell
    PS C:\> docker run -it -m 2GB --isolation=process microsoft/nanoserver powershell Get-ComputerInfo *memory*

    CsTotalPhysicalMemory      : 17064509440
    CsPhyicallyInstalledMemory : 16777216
    OsTotalVisibleMemorySize   : 16664560
    OsFreePhysicalMemory       : 14646720
    OsTotalVirtualMemorySize   : 19154928
    OsFreeVirtualMemory        : 17197440
    OsInUseVirtualMemory       : 1957488
    OsMaxProcessMemorySize     : 137438953344
    ```

- With `hyperv` isolation, Windows will create a utility VM that is big enough to hold the memory limit, plus the minimal OS needed to host the container. That size is reported as "Total Physical Memory."

    ```powershell
    PS C:\> docker run -it -m 2GB --isolation=hyperv microsoft/nanoserver powershell Get-ComputerInfo *memory*

    CsTotalPhysicalMemory      : 2683355136
    CsPhyicallyInstalledMemory :
    OsTotalVisibleMemorySize   : 2620464
    OsFreePhysicalMemory       : 2306552
    OsTotalVirtualMemorySize   : 2620464
    OsFreeVirtualMemory        : 2356692
    OsInUseVirtualMemory       : 263772
    OsMaxProcessMemorySize     : 137438953344
    ```


### <a name="sysctl"></a> Configure namespaced kernel parameters (sysctls) at runtime (--sysctl)

The `--sysctl` sets namespaced kernel parameters (sysctls) in the
container. For example, to turn on IP forwarding in the containers
network namespace, run this command:

```console
$ docker run --sysctl net.ipv4.ip_forward=1 someimage
```

> **Note**
>
> Not all sysctls are namespaced. Docker does not support changing sysctls
> inside of a container that also modify the host system. As the kernel
> evolves we expect to see more sysctls become namespaced.

#### Currently supported sysctls

IPC Namespace:

- `kernel.msgmax`, `kernel.msgmnb`, `kernel.msgmni`, `kernel.sem`,
  `kernel.shmall`, `kernel.shmmax`, `kernel.shmmni`, `kernel.shm_rmid_forced`.
- Sysctls beginning with `fs.mqueue.*`
- If you use the `--ipc=host` option these sysctls are not allowed.

Network Namespace:

- Sysctls beginning with `net.*`
- If you use the `--network=host` option using these sysctls are not allowed.