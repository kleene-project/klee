## Examples
```console
$ klee create -n mynet -l ipnet FreeBSD
da8f4c116490
$ klee network inspect my-net
{
  "network": {
    "gateway": "<auto>",
    "gateway6": "<auto>",
    "icc": true,
    "id": "cb9e8681e036",
    "interface": "mynet",
    "internal": false,
    "name": "mynet",
    "nat": "em0",
    "subnet": "10.2.3.0/24",
    "subnet6": "",
    "type": "bridge"
  },
  "network_endpoints": [
    {
      "container_id": "da8f4c116490",
      "epair": null,
      "id": "0b534000eeb7",
      "ip_address": "10.2.3.2",
      "ip_address6": "",
      "network_id": "cb9e8681e036"
    }
  ]
}
```
