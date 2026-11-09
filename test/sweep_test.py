import pytest

from testutils import (
    assert_clean_host_state,
    get_host_state,
    jail_info,
    listing_rows,
    run,
    shell,
    sweep_host_state,
)


def _basejail_snapshots():
    """Snapshot names (without dataset prefix) on the basejail dataset."""
    output = shell("zfs list -t snapshot -H -o name -d 1 zroot/kleene_basejail")
    return [line.split("@")[-1] for line in output.strip().split("\n") if line]


class TestSweep:
    def test_sweep_removes_every_leftover_class(self, create_testimage):
        # Residue a crashed or foreign-suite run would leave behind,
        # one instance per class the sweep must converge:
        #  - a running container (jail + metadata row)
        #  - a network (interface + metadata row)
        #  - a volume (dataset + metadata row)
        #  - an image no klee command can remove: cross-suite residue
        #  - an orphan container dataset (no metadata row at all)
        #  - a leaked kleene-named interface (no network row)
        #  - a clone-less basejail snapshot
        cid = run("container create --name sweepleak FreeBSD:latest /bin/sleep 100")[0]
        run(f"container start {cid}")
        run("network create --subnet 10.250.7.0/24 sweepnet")
        run("volume create sweepvol")
        run("image create -t leaky:residue zfs-clone zroot/kleene_basejail")
        shell(
            "zfs clone "
            f"zroot/kleene_basejail@{_basejail_snapshots()[0]} "
            "zroot/kleene/container/feedfacefeed"
        )
        shell("ifconfig tap create name kleene99")
        shell("zfs snapshot zroot/kleene_basejail@cloneless-leftover")

        sweep_host_state()

        baseline = get_host_state()
        assert_clean_host_state(baseline)

        # convergent: a second sweep over the now-clean host is a no-op
        sweep_host_state()
        assert_clean_host_state(get_host_state())

        # every listing is empty (FreeBSD:latest is class-scoped, created
        # outside this test -- hence not in the listings checked here)
        assert listing_rows(run("container ls -a")) == []
        assert listing_rows(run("network ls")) == []
        assert listing_rows(run("volume ls")) == []
        assert jail_info()["jail-information"]["jail"] == []

        # no kleene* interfaces remain
        interfaces = [i for i in shell("ifconfig -l").split() if i.startswith("kleene")]
        assert interfaces == []

        # no clone-less basejail snapshots remain
        output = shell("zfs list -t snapshot -H -o name,clones -d 1 zroot/kleene_basejail")
        cloneless = [line for line in output.strip().split("\n") if line and line.split("\t")[1] == "-"]
        assert cloneless == []
