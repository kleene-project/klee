import subprocess
import time

from testutils import (
    shell,
    jail_info,
    create_container,
    extract_exec_id,
    remove_all_containers,
    container_stopped_msg,
    remove_container,
    inspect,
    prune,
    run,
)


TEST_IMG = "FreeBSD:testing"


class TestContainerSubcommand:
    @classmethod
    def setup_class(cls):
        remove_all_containers()

    # pylint: disable=no-self-use
    def test_empty_container_listing_of_containers(self):
        empty_container_list(all_=False)
        empty_container_list(all_=True)

    def test_add_remove_and_list_containers(self):
        name = "test_adl_containers"
        container_id = create_container(name=name)
        assert len(container_id) == 12

        empty_container_list(all_=False)
        _header, _lines, container, *_ = run("container ls -a")
        assert container[1:13] == container_id

        container_id2, _ = run(f"container rm {name}")
        assert container_id2 == container_id

        empty_container_list()

    def test_invalid_container_name(self):
        def error(name):
            msg = "could not create container: {name} does not match /?[a-zA-Z0-9][a-zA-Z0-9_.-]+$\n"
            return msg.format(name=name)

        def cmd(name):
            cmd = "container create --name {} FreeBSD:testing"
            return "\n".join(run(cmd.format(name), exit_code=1))

        assert error(".test") == cmd(".test")
        assert error("-test") == cmd("-test")
        assert error("tes:t") == cmd("tes:t")

    def test_remove_running_container(self):
        name = "remove_running_container"
        container_id = create_container(name=name, command="sleep 10")
        run(f"container start --detach {container_id}")
        assert [container_id, ""] == run(f"container rm --force {container_id}")

    def test_inspect_container(self):
        name = "test_container_inspect"
        container_id = create_container(name=name)
        assert inspect("container", "notexist") == "container not found"
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["name"] == name
        remove_container(container_id)

    def test_restarting_container(self):
        container_id = create_container(name="test_restart", command="/bin/sleep 5")
        run(f"container start -d {container_id}")
        time.sleep(0.5)
        jails = jail_info()
        first_jid = jails["jail-information"]["jail"][0]["jid"]
        result = run(f"container restart {container_id}")
        assert result[0] == container_id
        jails = jail_info()
        after_jid = jails["jail-information"]["jail"][0]["jid"]
        assert first_jid + 1 == after_jid
        run(f"container stop {container_id}")

    def test_rename_container(self):
        name = "test_container_rename"
        container_id = create_container(name=name)
        container_id, _ = run(f"container rename {container_id} renamed")
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["name"] == "renamed"

    def test_update_container(self):
        name = "test_container_update"
        container_id = create_container(name=name)
        run(f"container update --env TEST=lol {container_id} /bin/sleep 10")
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["env"] == ["TEST=lol"]
        assert container_endpoints["container"]["cmd"] == ["/bin/sleep", "10"]

    def test_prune_container(self):
        remove_all_containers()
        name1 = "test_container_prune1"
        name2 = "test_container_prune1"
        container_id1 = create_container(name=name1)
        container_id2 = create_container(name=name2)
        assert prune("container") == [container_id1, container_id2]

    def test_remove_container_by_id(self):
        name = "test_remove"
        container_id1 = create_container()
        container_id2 = create_container(name=name)
        container_id1_again = remove_container(container_id1)
        container_id2_again = remove_container(container_id2)
        assert container_id1 == container_id1_again
        assert container_id2 == container_id2_again

    def test_remove_container_twice(self):
        container_id1 = create_container()
        assert container_id1 == remove_container(container_id1)
        assert ["no such container", ""] == run(f"container rm {container_id1}")

    def test_starting_and_stopping_a_container_and_list_containers(self):
        container_id = create_container(name="test_start_stop", command="/bin/sleep 10")
        succes_msg, _newline = run(f"container start -d {container_id}")
        assert "created execution instance " == succes_msg[:27]
        assert container_is_running(container_id)
        assert (container_id,) == container_list(all_=False)
        container_id_again, _ = run(f"container stop {container_id}")
        assert container_id == container_id_again
        assert not container_is_running(container_id)
        assert not container_list(all_=False)
        container_id_again = remove_container(container_id)
        assert container_id == container_id_again

    def test_container_referencing(self):
        name = "test_container_referencing"
        container_id = create_container(name=name, command="/bin/sleep 10")
        succes_msg, _newline = run(f"container start -d {container_id[:8]}")
        assert "created execution instance " == succes_msg[:27]
        assert container_is_running(container_id)
        container_id_again, _ = run(f"container stop {container_id[:8]}")
        assert container_id == container_id_again
        remove_container(container_id)

    def test_default_drivers_for_containers(self):
        # Creating a container not connected to a network without using the `--driver` option
        run("create --name DefaultDriverHost FreeBSD:testing")
        container_inspect = inspect("container", "DefaultDriverHost")
        assert "host" == container_inspect["container"]["network_driver"]

        # Creating a container connected to a network without using the '--driver' option
        run("network create --subnet 10.45.56.0/24 testnet")
        run("create --network testnet --name DefaultDriverIPNet FreeBSD:testing")
        container_inspect = inspect("container", "DefaultDriverIPNet")
        assert "ipnet" == container_inspect["container"]["network_driver"]

    def test_start_attached_container(self):
        name = "test_attached_container"
        container_id = create_container(name=name, command="/usr/bin/uname")
        container_output = run(f"container start {container_id}")
        exec_id = extract_exec_id(container_output)
        expected_output = [
            f"created execution instance {exec_id}",
            "FreeBSD",
            "",
            container_stopped_msg(exec_id),
            "",
        ]
        assert container_output == expected_output
        remove_container(container_id)

    def test_running_containers_with_mounts(self):
        output = run(
            f"container create -m too:many:colons:here {TEST_IMG}", exit_code=125
        )
        assert output == [
            "invalid mount format 'too:many:colons:here'. Max 3 elements seperated by ':'.",
            "",
        ]

        output = run(
            f"container create -m too-few-colons-here {TEST_IMG}", exit_code=125
        )
        assert output == [
            "invalid mount format 'too-few-colons-here'. Must have at least 2 elements ",
            "seperated by ':'.",
            "",
        ]
        output = run(
            f"container run -m new_volume:/kl_mount_test:invalid {TEST_IMG} ls /kl_mount_test",
            exit_code=125,
        )
        assert output == [
            "invalid mount format 'new_volume:/kl_mount_test:invalid'. Last element should be",
            "either 'ro' or 'rw'.",
            "",
        ]

    def test_run_a_container_with_readonly_volume(self):
        output = run(
            f"container run -m new_volume:/kl_mount_test:ro {TEST_IMG} touch /kl_mount_test/test.txt"
        )
        assert output[2] == "touch: /kl_mount_test/test.txt: Read-only file system"

    def test_run_a_container_with_nullfs_mount(self):
        shell("rm /mnt/text.txt")
        output = run(
            f"container run -m /mnt:/kl_mount_test {TEST_IMG} touch /kl_mount_test/test.txt"
        )
        expected_exit = "container exited with exit-code 0"
        idx = -len(expected_exit)
        assert output[3][idx:] == expected_exit
        assert shell("cat /mnt/test.txt").returncode == 0
        assert shell("cat /mnt/test.txt").stdout == b""


def container_is_running(container_id):
    # If grep have at least one match it returns statuscode 0, otherwise 1
    result = subprocess.run(
        ["/bin/sh", "-c", f"jls | grep {container_id}"], check=False
    )
    return result.returncode == 0


def empty_container_list(all_=True):
    expected_output = [
        " CONTAINER ID    NAME   IMAGE   COMMAND   CREATED   STATUS   JID ",
        "─────────────────────────────────────────────────────────────────",
        "",
    ]

    if all_:
        output = run("container ls -a")
    else:
        output = run("container ls")

    assert output == expected_output


def container_list(all_=True):
    """Returns a tuple of container_ids from the 'container ls' command"""
    if all_:
        output = run("container ls -a")
    else:
        output = run("container ls")
    output = output[2:-2]  # exclude header + postfixed line-endings
    container_ids = [row[1:13] for row in output[:-1]]
    return tuple(container_ids)
