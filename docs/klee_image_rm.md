## Examples
You can remove an image using its ID, a unique initial segment of the ID, or its nametag.
If a name without a tag is supplied, Kleened will assume the tag is `latest`.

It is not possible to remove an image if any containers or other images is
based on it.

```console
$ klee image rm 4a103f27dad8 FreeBSD:testing FreeBSD
4a103f27dad8
422100eb65cc
27363da77910
```
