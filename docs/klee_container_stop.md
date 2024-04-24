## Description
Stopping containers using `klee container stop`, which is based on the FreeBSD CLI-tool `jail`
under the hood. See the [`jails(8)` manual pages](https://man.freebsd.org/cgi/man.cgi?query=jail) for details.

## Examples
```console
$ klee stop my_container1 6e33 my_container3 2d6d265811f4
f41d1fabb009
6e33265811f4
27363da77910
2d6d265811f4
```
