## Examples
You can remove an image using its ID or its nametag.
If just a name is supplied, Kleened will assume the tag `latest`.

It is not possible to remove an image if any containers or other images is
based on it.

```console
$ klee image rm 4a103f27dad8 FreeBSD:testing FreeBSD
4a103f27dad8
422100eb65cc
27363da77910
```
