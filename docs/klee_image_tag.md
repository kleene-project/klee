## Description
Redefine the nametag of an image.

A nametag must be valid ASCII and may contain lowercase and uppercase letters,
digits, underscores, periods and dashes. A nametag may not start with a
period or a dash and may contain a maximum of 128 characters. The `name` and
`tag` components are seperated by `:`.

## Examples

### Tag an image referenced by ID

To tag an image with ID "2e91f95bf959":

```console
$ klee tag 0e5574283393 13.2-STABLE/base
```

Note that since a `tag` is not specified Kleened sets it to `latest`,
i.e., `13.2-STABLE/base:latest`.

### Tag an image referenced by name

To tag a local image with FreeBSD additional releng `REVISION` information:

```console
$ klee tag FreeBSD-13.1-RELEASE FreeBSD-13.1-RELEASE:fc952ac2212
```

Note that since a `tag` is not specified Kleened sets it to `latest`.

### Tag an image referenced by nametag

Re-tag an image and replace tag "test" with "version1.0.test":

```console
$ docker tag nginx:test nginx:version1.0.test
```
