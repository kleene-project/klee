## Description
Import an image into Kleened from an OCI image layout archive.

The `ARCHIVE` argument is either a URL (an `https` address) or a path to a file
in the filesystem of the host where Kleened is running. The archive is expected
to be a `.txz` or `.tar` file containing an
[OCI image layout](https://github.com/opencontainers/image-spec/blob/main/image-layout.md),
i.e. an `oci-layout` file, an `index.json` and a `blobs/` directory. The
container images published on
[download.freebsd.org](https://download.freebsd.org/releases/OCI-IMAGES/)
have this layout.

The result is a regular Kleene image: it can be used to create containers and
as the parent image in a `FROM`-instruction when building other images.

Use `-t`, `--tag`, to name the imported image using the `name:tag` format. If
the tag is omitted, `latest` is assumed.

If the archive's index contains more than one manifest, for instance an image
published for several architectures, `-p`, `--platform`, selects which one to
import by `os/architecture` (e.g. `freebsd/amd64`). If the option is not used,
the first manifest in the index is imported.

Importing the same archive content under the same `name:tag` more than once is
idempotent: instead of storing a duplicate, the already imported image is
returned.

Kleened picks up the image configuration stored in the archive, so the fields
`Cmd`, `Entrypoint`, `Env`, `User`, `WorkingDir` and `Labels` are preserved on
the image. Containers started from the image inherit the entrypoint and command
and start in the image's working directory.

## Examples

### Import a local archive

```console
$ klee image import -t freebsd-static:15.0 /tmp/FreeBSD-15.0-RELEASE-amd64-container-image-static.txz
extracting layer 1/1 (7291b618e0df)...
image imported
1a2b3c4d5e6f
```

The archive is read from `/tmp` on the host running Kleened. If `klee` is used
from another machine, keep this in mind and use a path that exists on the
Kleened host.

### Import an archive from a URL

```console
$ klee image import -t freebsd-runtime:15.0 https://download.freebsd.org/releases/OCI-IMAGES/15.0-RELEASE/amd64/Latest/FreeBSD-15.0-RELEASE-amd64-container-image-runtime.txz
extracting layer 1/1 (7291b618e0df)...
image imported
7c8d9e0f1a2b
```

Kleened fetches the archive itself, so the URL has to be reachable from the
host running Kleened.

### Run a container from the imported image

```console
$ klee container run freebsd-runtime:15.0 /bin/sh -c "uname -a"
FreeBSD 48e1a4e37aea 15.1-RELEASE-p3 FreeBSD 15.1-RELEASE-p3 releng/15.1-n283562-88e7371d9dcf GENERIC amd64
```

Since the command from the image is inherited when none is given, and the
image's working directory is used for shell commands, the container behaves
like it would with any other Kleene image.
