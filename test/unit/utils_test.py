"""Unit tests for klee.utils' pure option-decoding helpers.

These need no kleened, no root, no jails and no ZFS -- see the 'unit' marker in
pyproject.toml. They are the fast tier: run them with 'make test-unit'.
"""

import pytest

from klee.utils import decode_mount, decode_public_ports

pytestmark = pytest.mark.unit


class TestDecodeMount:
    @pytest.mark.parametrize(
        "mount,expected",
        [
            (
                "myvolume:/mnt",
                {
                    "type": "volume",
                    "source": "myvolume",
                    "destination": "/mnt",
                    "read_only": False,
                },
            ),
            (
                "/host/dir:/mnt",
                {
                    "type": "nullfs",
                    "source": "/host/dir",
                    "destination": "/mnt",
                    "read_only": False,
                },
            ),
            (
                "/host/dir:/mnt:ro",
                {
                    "type": "nullfs",
                    "source": "/host/dir",
                    "destination": "/mnt",
                    "read_only": True,
                },
            ),
            (
                "myvolume:/mnt:rw",
                {
                    "type": "volume",
                    "source": "myvolume",
                    "destination": "/mnt",
                    "read_only": False,
                },
            ),
        ],
    )
    def test_valid_mounts(self, mount, expected):
        assert decode_mount(mount) == expected

    def test_leading_slash_selects_nullfs_over_volume(self):
        # The only thing distinguishing the two mount types is the leading slash.
        assert decode_mount("data:/mnt")["type"] == "volume"
        assert decode_mount("/data:/mnt")["type"] == "nullfs"

    @pytest.mark.parametrize(
        "mount",
        [
            "too-few-colons-here",  # fewer than 2 sections
            "a:b:c:d",  # more than 3 sections
            "/src:/dst:readonly",  # third section must be exactly ro or rw
            "/src:/dst:RO",  # and is case-sensitive
        ],
    )
    def test_invalid_mounts_exit_125(self, mount):
        with pytest.raises(SystemExit) as excinfo:
            decode_mount(mount)
        assert excinfo.value.code == 125


class TestDecodePublicPorts:
    @pytest.mark.parametrize(
        "spec,expected",
        [
            # <HOST-PORT>
            (
                "8080",
                {
                    "interfaces": [],
                    "host_port": "8080",
                    "container_port": "8080",
                    "protocol": "tcp",
                },
            ),
            # <HOST-PORT>:<CONTAINER-PORT>
            (
                "8080:80",
                {
                    "interfaces": [],
                    "host_port": "8080",
                    "container_port": "80",
                    "protocol": "tcp",
                },
            ),
            # <HOST-PORT>:<CONTAINER-PORT>/<PROTOCOL>
            (
                "8080:80/udp",
                {
                    "interfaces": [],
                    "host_port": "8080",
                    "container_port": "80",
                    "protocol": "udp",
                },
            ),
            # <INTERFACE>:<HOST-PORT>:<CONTAINER-PORT>
            (
                "em0:8080:80",
                {
                    "interfaces": ["em0"],
                    "host_port": "8080",
                    "container_port": "80",
                    "protocol": "tcp",
                },
            ),
            # <INTERFACE>:<HOST-PORT>:<CONTAINER-PORT>/<PROTOCOL>
            (
                "em0:8080:80/udp",
                {
                    "interfaces": ["em0"],
                    "host_port": "8080",
                    "container_port": "80",
                    "protocol": "udp",
                },
            ),
        ],
    )
    def test_valid_specs(self, spec, expected):
        assert list(decode_public_ports([spec])) == [expected]

    def test_bare_port_maps_to_itself(self):
        (result,) = decode_public_ports(["4000"])
        assert result["host_port"] == result["container_port"] == "4000"

    def test_several_specs_decode_independently(self):
        results = list(decode_public_ports(["8080", "em0:9000:90/udp"]))
        assert [r["host_port"] for r in results] == ["8080", "9000"]
        assert [r["protocol"] for r in results] == ["tcp", "udp"]
        assert [r["interfaces"] for r in results] == [[], ["em0"]]

    def test_too_many_colon_separated_sections_exits(self):
        with pytest.raises(SystemExit):
            list(decode_public_ports(["em0:8080:80:extra"]))
