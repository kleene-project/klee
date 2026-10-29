## Description

Pull an image into Kleened from an OCI distribution registry.

The `REF` argument is an image reference on the form
`[registry/]repository[:tag][@digest]`, for instance
`ghcr.io/freebsd/freebsd-static:15.0`. The image is fetched over HTTPS from
the registry, so the host running Kleened needs network access to it.

References that do not name a registry resolve against the default registry,
`docker.io`. `nginx` becomes `docker.io/library/nginx` and
`freebsd/freebsd-runtime` becomes `docker.io/freebsd/freebsd-runtime`.

The result is a regular Kleene image: it can be used to create containers and
as the parent image in a `FROM`-instruction when building other images. It is
tagged `repository:tag` from the reference, which means the registry host is
not part of the image name: pulling `ghcr.io/freebsd/freebsd-static:15.0`
gives the image `freebsd/freebsd-static:15.0`. If the tag is omitted,
`latest` is assumed.

If the registry serves a multi-platform image index, `-p`, `--platform`,
selects which manifest to pull by `os/architecture` (e.g. `freebsd/arm64`).
If the option is not used, the manifest matching the host's own
`os/architecture` (from `uname(1)`) is pulled.

Pulling the same manifest digest more than once is idempotent: instead of
downloading it again, the already stored image is returned.

Every downloaded blob (manifest, config and layers) is verified against its
sha256 digest, and a mismatch aborts the pull. When the downloaded set is
assembled into an image, all blobs are verified once more.

## Examples

### Pull an image from a registry

```console
$ klee image pull ghcr.io/freebsd/freebsd-static:15.0
downloading layer 1/3 (abcdef123456)...
extracting layer 1/3 (abcdef123456)...
downloading layer 2/3 (7890abcdef12)...
extracting layer 2/3 (7890abcdef12)...
downloading layer 3/3 (34567890abcd)...
extracting layer 3/3 (34567890abcd)...
image pulled
1a2b3c4d5e6f
```

The progress messages are streamed as the layers are downloaded and
extracted, and the image id is printed when the pull completes.

### Pull from the default registry

```console
$ klee image pull freebsd/freebsd-static:15.0     # resolves to docker.io
```

Since no registry is named, the reference resolves to `docker.io` and the
image is stored as `freebsd/freebsd-static:15.0`.

### Use the pulled image

```console
$ klee pull ghcr.io/freebsd/freebsd-static:15.0
$ klee run freebsd/freebsd-static:15.0 /bin/sh
```

`klee pull` is a top-level shortcut for `klee image pull`. The image is
referenced by its Kleene name, without the registry host, like it would be
with any other Kleene image.
