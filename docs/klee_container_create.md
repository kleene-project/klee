## Description
The `docker container create` (or shorthand: `docker create`) command creates a
new container from the specified image, without starting it.

When creating a container, the docker daemon creates a writeable container layer
over the specified image and prepares it for running the specified command.  The
container ID is then printed to `STDOUT`.  This is similar to `docker run -d`
except the container is never started. You can then use the `docker container start`
(or shorthand: `docker start`) command to start the container at any point.

This is useful when you want to set up a container configuration ahead of time
so that it is ready to start when you need it. The initial status of the
new container is `created`.

The `docker create` command shares most of its options with the `docker run`
command (which performs a `docker create` before starting it). Refer to the
[`docker run` command](run.md) section and the [Docker run reference](../run.md)
for details on the available flags and options.

## Examples
### Create and start a container

The following example creates an interactive container with a pseudo-TTY attached,
then starts the container and attaches to it:

```console
$ docker container create -i -t --name mycontainer alpine
6d8af538ec541dd581ebc2a24153a28329acb5268abe5ef868c1f1a261221752

$ docker container start --attach -i mycontainer
/ # echo hello world
hello world
```

The above is the equivalent of a `docker run`:

```console
$ docker run -it --name mycontainer2 alpine
/ # echo hello world
hello world
```

### Initialize volumes

Container volumes are initialized during the `docker create` phase
(i.e., `docker run` too). For example, this allows you to `create` the `data`
volume container, and then use it from another container:

```console
$ docker create -v /data --name data ubuntu

240633dfbb98128fa77473d3d9018f6123b99c454b3251427ae190a7d951ad57

$ docker run --rm --volumes-from data ubuntu ls -la /data

total 8
drwxr-xr-x  2 root root 4096 Dec  5 04:10 .
drwxr-xr-x 48 root root 4096 Dec  5 04:11 ..
```

Similarly, `create` a host directory bind mounted volume container, which can
then be used from the subsequent container:

```console
$ docker create -v /home/docker:/docker --name docker ubuntu

9aa88c08f319cd1e4515c3c46b0de7cc9aa75e878357b1e96f91e2c773029f03

$ docker run --rm --volumes-from docker ubuntu ls -la /docker

total 20
drwxr-sr-x  5 1000 staff  180 Dec  5 04:00 .
drwxr-xr-x 48 root root  4096 Dec  5 04:13 ..
-rw-rw-r--  1 1000 staff 3833 Dec  5 04:01 .ash_history
-rw-r--r--  1 1000 staff  446 Nov 28 11:51 .ashrc
-rw-r--r--  1 1000 staff   25 Dec  5 04:00 .gitconfig
drwxr-sr-x  3 1000 staff   60 Dec  1 03:28 .local
-rw-r--r--  1 1000 staff  920 Nov 28 11:51 .profile
drwx--S---  2 1000 staff  460 Dec  5 00:51 .ssh
drwxr-xr-x 32 1000 staff 1140 Dec  5 04:01 docker
```