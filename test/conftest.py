import pytest

from testutils import run, shell

# pylint: disable=unused-argument
@pytest.fixture(scope="class")
def create_testimage():
    run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
    yield None
    run("rmi FreeBSD:latest")


@pytest.fixture(scope="class")
def host_state():
    host_state = {"zfs": set(shell("zfs list -H -o name -r zroot/kleene").split("\n"))}

    yield host_state

    zfs_now = set(shell("zfs list -H -o name -r zroot/kleene").split("\n"))
    assert host_state["zfs"] == zfs_now


@pytest.fixture()
def cleanup(create_testimage, host_state):
    yield host_state
    run("container prune -f")
    run("network prune -f")


@pytest.fixture()
def testimage(create_testimage, host_state):
    yield host_state


@pytest.fixture()
def testimage_and_cleanup(create_testimage, host_state, cleanup):
    yield host_state
