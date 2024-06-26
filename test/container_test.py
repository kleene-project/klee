from functools import partial
from multiprocessing import Process
import subprocess
import json
import time

from testutils import (
    EMPTY_CONTAINER_LIST,
    shell,
    shell_raw,
    jail_info,
    create_container,
    list_containers,
    extract_exec_id,
    container_stopped_msg,
    inspect,
    prune,
    run,
)


TEST_IMG = "FreeBSD"


# pylint: disable=no-self-use, unused-argument
class TestContainerSubcommand:
    def test_empty_container_listing_of_containers(self, testimage_and_cleanup):
        empty_container_list(all_=False)
        empty_container_list(all_=True)

    def test_add_remove_and_list_containers(self, testimage_and_cleanup):
        name = "test_adl_containers"
        container_id = create_container(name=name)
        assert len(container_id) == 12

        empty_container_list(all_=False)
        _header, _lines, container, *_ = run("container ls -a")
        assert container[1:13] == container_id

        container_id2, _ = run(f"container rm {name}")
        assert container_id2 == container_id

        empty_container_list()

    def test_invalid_container_name(self, testimage_and_cleanup):
        def error(name):
            msg = "could not create container: {name} does not match /?[a-zA-Z0-9][a-zA-Z0-9_.-]+$\n"
            return msg.format(name=name)

        def cmd(name):
            cmd = "container create --name {} FreeBSD"
            return "\n".join(run(cmd.format(name), exit_code=1))

        assert error(".test") == cmd(".test")
        assert error("-test") == cmd("-test")
        assert error("tes:t") == cmd("tes:t")

    def test_invalid_network_driver(self, testimage_and_cleanup):
        output = run("run -l lolnet FreeBSD /bin/ls", exit_code=1)
        error = "Error! Could not validate container configuration: 'lolnet' is not a valid ContainerConfigNetworkDriver"
        assert error == "".join(output)

    def test_remove_running_container(self, testimage_and_cleanup):
        name = "remove_running_container"
        container_id = create_container(name=name, command="sleep 10")
        run(f"container start --detach {container_id}")
        assert [container_id, ""] == run(f"container rm --force {container_id}")

    def test_inspect_container(self, testimage_and_cleanup):
        name = "test_container_inspect"
        container_id = create_container(name=name)
        assert inspect("container", "notexist") == "container not found"
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["name"] == name
        run("rmc {container_id}")

    def test_restarting_container(self, testimage_and_cleanup):
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

    def test_rename_container(self, testimage_and_cleanup):
        name = "test_container_rename"
        container_id = create_container(name=name)
        container_id, _ = run(f"container rename {container_id} renamed")
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["name"] == "renamed"

    def test_update_container_cmd_and_env(self, testimage_and_cleanup):
        name = "test_container_update"
        container_id = create_container(name=name)
        run(f"container update --env TEST=lol {container_id} /bin/sleep 10")
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["env"] == ["TEST=lol"]
        assert container_endpoints["container"]["cmd"] == ["/bin/sleep", "10"]

    def test_update_container_restart_policy(self, testimage_and_cleanup):
        name = "update_restart_policy"
        container_id = create_container(name=name)
        run(f"container update --restart on-startup {container_id}")
        container_endpoints = inspect("container", container_id)
        assert container_endpoints["container"]["restart_policy"] == "on-startup"

    def test_prune_container(self, testimage_and_cleanup):
        name1 = "test_container_prune1"
        name2 = "test_container_prune2"
        container_id1 = create_container(name=name1)
        container_id2 = create_container(name=name2)
        assert prune("container") == [container_id1, container_id2]

    def test_cannot_prune_persisted_container(self, testimage_and_cleanup):
        name1 = "prune_persist1"
        name2 = "prune_persist2"
        container_id1, _ = run(f"create --name {name1} FreeBSD")
        container_id2, _ = run(f"create --persist --name {name2} FreeBSD")
        assert prune("container") == [container_id1]
        run(f"rmc {container_id2}")

    def test_remove_container_by_id(self, testimage_and_cleanup):
        name = "test_remove"
        container_id1 = create_container()
        container_id2 = create_container(name=name)
        container_id1_again, *_ = run(f"rmc {container_id1}")
        container_id2_again, *_ = run(f"rmc {container_id2}")
        assert container_id1 == container_id1_again
        assert container_id2 == container_id2_again

    def test_remove_container_twice(self, testimage_and_cleanup):
        container_id1 = create_container()
        container_id1_again, *_ = run(f"rmc {container_id1}")
        assert container_id1 == container_id1_again
        assert ["no such container", ""] == run(f"container rm {container_id1}")

    def test_starting_and_stopping_a_container_and_list_containers(
        self, testimage_and_cleanup
    ):
        container_id = create_container(name="test_start_stop", command="/bin/sleep 10")
        succes_msg, _newline = run(f"container start -d {container_id}")
        assert "created execution instance " == succes_msg[:27]
        assert container_is_running(container_id)
        container, *_ = list_containers(all_=False)
        assert container_id == container.id
        container_id_again, _ = run(f"container stop {container_id}")
        assert container_id == container_id_again
        assert not container_is_running(container_id)
        assert not list_containers(all_=False)
        container_id_again, *_ = run(f"rmc {container_id}")
        assert container_id == container_id_again

    def test_container_referencing(self, testimage_and_cleanup):
        name = "test_container_referencing"
        container_id = create_container(name=name, command="/bin/sleep 10")
        succes_msg, _newline = run(f"container start -d {container_id[:8]}")
        assert "created execution instance " == succes_msg[:27]
        assert container_is_running(container_id)
        container_id_again, _ = run(f"container stop {container_id[:8]}")
        assert container_id == container_id_again
        run(f"rmc {container_id}")

    def test_attached_client_exits_abruptly_and_container_process_continues(
        self, testimage_and_cleanup
    ):
        # Only the process '/usr/sbin/jail ...' is killed, not the jailed process itself
        def listening_port_exist(port):
            output = json.loads(shell("netstat --libxo json -l4na -p tcp"))
            for socket in output["statistics"]["socket"]:
                if socket["local"]["port"] == port:
                    return True

            return False

        command = "run --name myname FreeBSD /bin/sh -c".split(" ") + ["nc -l 4000"]
        nc_server = Process(target=run, args=(command,), daemon=False)
        nc_server.start()
        time.sleep(0.5)
        assert nc_server.is_alive()
        assert listening_port_exist("4000")
        assert nc_server.is_alive()
        nc_server.terminate()
        time.sleep(0.5)
        assert not nc_server.is_alive()

        result = shell_raw("nc -v -z localhost 4000")
        assert (
            b"Connection to localhost 4000 port [tcp/*] succeeded!\n" == result.stderr
        )
        run("stop myname")

    def test_default_drivers_for_containers(self, testimage_and_cleanup):
        # Creating a container not connected to a network without using the `--driver` option
        run("create --name DefaultDriverHost FreeBSD:latest")
        container_inspect = inspect("container", "DefaultDriverHost")
        assert "host" == container_inspect["container"]["network_driver"]

        # Creating a container connected to a network without using the '--driver' option
        run("network create --subnet 10.45.56.0/24 testnet")
        run("create --network testnet --name DefaultDriverIPNet FreeBSD:latest")
        container_inspect = inspect("container", "DefaultDriverIPNet")
        assert "ipnet" == container_inspect["container"]["network_driver"]

    def test_start_attached_container(self, testimage_and_cleanup):
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
        run("rmc {container_id}")

    def test_run_a_container_with_readonly_volume(self, testimage_and_cleanup):
        output = run(
            f"container run --name voltest1 -m new_volume:/kl_mount_test:ro {TEST_IMG} touch /kl_mount_test/test.txt"
        )
        assert output[2] == "touch: /kl_mount_test/test.txt: Read-only file system"
        run("rmc voltest1")
        run("volume rm new_volume")

    def test_run_a_container_with_nullfs_directory_mount(self, testimage_and_cleanup):
        shell("rm /mnt/text.txt")
        output = run(
            f"container run -m /mnt:/kl_mount_test {TEST_IMG} touch /kl_mount_test/test.txt"
        )
        expected_exit = "container exited with exit-code 0"
        idx = -len(expected_exit)
        assert output[3][idx:] == expected_exit
        assert shell_raw("cat /mnt/test.txt").returncode == 0
        assert shell("cat /mnt/test.txt") == ""

    def test_run_a_container_with_nullfs_file_mount(self, testimage_and_cleanup):
        shell("rm /mnt/testfile.txt")
        shell("echo 'hello' > /mnt/testfile.txt")
        output = run(
            f"container run --name mtest1 -m /mnt/testfile.txt:/mounted_file_test {TEST_IMG} cat /mounted_file_test"
        )
        assert output[2] == "hello"

        # Create directory path of destination
        output = run(
            f"container run --name mtest2 -m /mnt/testfile.txt:/create_me/mounted_file_test {TEST_IMG} cat /create_me/mounted_file_test"
        )
        assert output[2] == "hello"
        run("rmc mtest1 mtest2")
        shell("rm /mnt/testfile.txt")

    def test_mountpoint_metadata_persist_when_container_stops(
        self, testimage_and_cleanup
    ):
        run(f"create --name mountmetadata -m /mnt:/host_mnt {TEST_IMG} ls")
        container_info = inspect("container", "mountmetadata")
        container_id = container_info["container"]["id"]
        expected_endpoint = {
            "container_id": container_id,
            "destination": "/host_mnt",
            "read_only": False,
            "source": "/mnt",
            "type": "nullfs",
        }
        assert [expected_endpoint] == container_info["container_mountpoints"]
        container_info = inspect("container", "mountmetadata")
        assert [expected_endpoint] == container_info["container_mountpoints"]
        run("rmc mountmetadata")

        run(f"container run --name mountmetadata -m /mnt:/host_mnt {TEST_IMG} sleep 10")
        run("stop mountmetadata")

        container_info = inspect("container", "mountmetadata")
        expected_endpoint["container_id"] = container_info["container"]["id"]
        assert [expected_endpoint] == container_info["container_mountpoints"]

    def test_try_running_containers_with_invalid_mounts(self, testimage_and_cleanup):
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


def container_is_running(container_id):
    # If grep have at least one match it returns statuscode 0, otherwise 1
    result = subprocess.run(
        ["/bin/sh", "-c", f"jls | grep {container_id}"], check=False
    )
    return result.returncode == 0


def empty_container_list(all_=True):
    if all_:
        output = run("container ls -a")
    else:
        output = run("container ls")

    assert output == EMPTY_CONTAINER_LIST
