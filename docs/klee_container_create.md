## Description
The `klee container create` (or shorthand: `klee create`) command creates a
new container from the specified image, without starting it.

This command is useful when you want to set up a container configuration ahead of time
so that it is ready to start when you need it.

When creating a container, Kleened creates a ZFS dataset based
on the image and prepares it for running the specified command.
If no command is specified, Kleened uses the `CMD` specified in the image.
The container ID is then printed to `STDOUT`.

### Specifying IMAGE
The `IMAGE` argument takes the following two forms:

- `<image_id>[:@<snapshot_id>]`
- `<image_name>[:<tag>][:@<snapshot_id>]`

If `<tag>` is omitted `latest` is assumed. For example,

- `FreeBSD` means the image `FreeBSD` with tag `latest`
- `FreeBSD:13.2-STABLE` means the image `FreeBSD` with tag `13.2-STABLE`
- `FreeBSD:base:@6b3c821605d4` means the `FreeBSD:base` image but create the container from the snapshot `6b3c821605d4`
- `48fa55889b0f` use the image having ID `48fa55889b0f`
- `48fa55889b0f:@2028818d6f06` use the image as above but create the container from the snapshot `2028818d6f06`

For more information about snapshots see the [Build snapshots](/build/building/snapshots/) section.

### Specifying mounts
When creating containers it is also possible to mount volumes/directories/files
into the container using one or more `--mount/-m  <mount>` flags. `<mount>` must use
the following syntax:

```console
SOURCE:DESTINATION[:rw|ro]
```

where

- `SOURCE` can be either a volume name or an absolute path on the host system.
  If `SOURCE` starts with '`/`' it is interpreted as a host path.
  If a volume name is specified, and the volume does not exist, it will be created.
- `DESTINATION` is the path of the mount within the container. If it does not exist it
  will be created.
- Optionally, if the mount is postfixed with `:ro` or `:rw` the mount will be read-only
  or read-write, respectively. If omitted, `:rw` is assumed.

For example:

- `klee container create -m logs:/var/log ...` mount a volume named `logs` into the container at `/var/log`.
- `klee container create -m my_archive:/archive:ro ...` create a read-only `archive` mountpoint in the
  container root for the `my_archive` volume.
- `klee container create -m /home/some_user:/home/some_user ...` mount the host directory `/home/some_user`
  into the same path within the container.

### Starting the container
You can then use the `klee container start`
(or shorthand: `klee start`) command to start the container at any point.
Combinining `klee container create` and `klee container start` is equivalent to
`klee container run`.

The `klee create` command shares most of its options with the `klee run`
command. Refer to the [`klee container run` command](container_run.md) section
for details on the available flags and options.

## Examples

More examples available at the [`klee container run` command](container_run.md) documentation.

### Create and start a container

The following example creates an interactive container with a pseudo-TTY attached,
then starts the container and attaches to it:

```console
$ klee container create --name mycontainer hello-world:latest
4d9d4e72a07f

$ klee container start -ait mycontainer
created execution instance 71c359af03f7
Hello World

executable 71c359af03f7 and its container exited with exit-code 0
```

The above is the equivalent of a `klee run`:

```console
$ klee container run -ait --name mycontainer hello-world:latest
6e33dbacde70
created execution instance 4eb13ad4c3a4
Hello World

executable 4eb13ad4c3a4 and its container exited with exit-code 0
```

### Initialize volumes

Container volumes can be automatically created during the `klee container create`
phase (and `klee container run` too):

```console
$ klee container create -v /data --name storage FreeBSD13.2-STABLE
5f8e437e5c95

$ klee volume ls
 VOLUME NAME    CREATED
──────────────────────────────
 6dedc1df7b42   10 secondsago
```
