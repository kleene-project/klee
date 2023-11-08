## Examples
### Remove a network

To remove the network named 'my-network':

```console
$ klee network rm my-net
422aec867d4e
```

### Remove multiple networks

To delete multiple networks in a single `klee network rm` command, provide
multiple network names, IDs, or initial segments of IDs:

```console
$ klee network rm my-net2 f4c88f269007 ec03
6129eb13a227
f4c88f269007
ec033436e65e
```

When you specify multiple networks, Klee attempts to delete each in turn.
If the deletion of one network fails, Klee stops deleting the remaining networks.
