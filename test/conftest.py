import pytest

from testutils import (
    assert_clean_host_state,
    get_host_state,
    run,
    sweep_host_state,
)

# pylint: disable=unused-argument


@pytest.fixture(scope="class")
def create_testimage():
    run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
    yield None
    run("rmi FreeBSD:latest")


@pytest.fixture()
def host_state():
    # sweep BEFORE snapshotting state to avoid  a dirty host state
    sweep_host_state()
    baseline = get_host_state()

    yield baseline

    sweep_host_state()
    assert_clean_host_state(baseline)


@pytest.fixture()
def cleanup(host_state):
    yield host_state
    sweep_host_state()


@pytest.fixture()
def prune_images(host_state):
    yield host_state
    run("image prune -a -f")


@pytest.fixture()
def cleanup_all(prune_images, cleanup):
    yield host_state


@pytest.fixture()
def testimage(create_testimage, host_state):
    yield host_state


@pytest.fixture()
def testimage_and_cleanup(create_testimage, host_state, cleanup):
    yield host_state


def pytest_sessionfinish(session, exitstatus):
    # the last test of a run has no next-test cleanup to rely on: leave
    # the host clean regardless of how the run ended
    try:
        sweep_host_state()
    except Exception as exc:  # noqa: BLE001 - never mask test results
        print(f"final sweep failed: {exc}")
