## Description
`klee image ls` (or, shorthand: `klee lsi`) will show all images.

Image snapshots, however, are not shown. Use [`klee image inspect`](/reference/klee/image_inspect/) instead.

## Examples
### List all images

```console
$ klee image ls
 ID             NAME                  TAG         CREATED
──────────────────────────────────────────────────────────────
 707f754571dd   hello-world           latest      4 hours ago
 1bf7491b3de3   myapp_debug           latest      4 hours ago
 d67864280076   nginx                 1.24.0_13   4 hours ago
 cecc28cf8ad4   FreeBSD-13.2-STABLE   latest      4 hours ago
```
