## Examples

Create a volume, mount it into a container, and inspect it:

```console
$ klee volume create data
data
$ klee run -m data:/data FreeBSD
5faf4811c124
created execution instance b00b2e926566

...container output here...

b00b2e926566 has exited with exit-code 0
$ klee volume inspect data
{
  "mountpoints": [
    {
      "container_id": "5faf4811c124",
      "destination": "/data",
      "read_only": false,
      "source": "data",
      "type": "volume"
    }
  ],
  "volume": {
    "created": "2024-04-18T10:00:45.138987Z",
    "dataset": "zroot/kleene/volumes/data",
    "mountpoint": "/zroot/kleene/volumes/data",
    "name": "data"
  }
}
```
