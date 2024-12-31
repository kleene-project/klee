import pytest
import TestHelper


class TestContainer:

    def test_create_remove_and_list_containers(self):
        assert TestHelper.container_list() == []

        container1 = TestHelper.container_successfully_create(
            {"name": "testcont"})
        img_id = TestHelper.get_image_id("FreeBSD:testing")
        assert container1.image_id == img_id

        container_list = TestHelper.container_list()
        assert any(
            c.id == container1.id and c.name == container1.name for c in container_list
        )

        container2 = TestHelper.container_successfully_create(
            {"name": "testcont2"})
        container_list = TestHelper.container_list()
        assert any(
            c.id == container2.id and c.name == container2.name for c in container_list
        )

        TestHelper.container_remove(container1.id)
        assert not any(
            c.id == container1.id for c in TestHelper.container_list()
        )

        TestHelper.container_remove(container2.id)
        assert TestHelper.container_list() == []

        with pytest.raises(Exception):
            TestHelper.container_remove(container2.id)

    def test_prune_containers(self):
        container1 = TestHelper.container_successfully_create(
            {"name": "testprune1", "cmd": ["/bin/sleep", "10"]}
        )
        container2 = TestHelper.container_successfully_create(
            {"name": "testprune2", "cmd": ["/bin/sleep", "10"]}
        )
        container3 = TestHelper.container_successfully_create(
            {"name": "testprune3", "cmd": ["/bin/sleep", "10"]}
        )

        exec_id = TestHelper.exec_create(container2.id)
        TestHelper.exec_valid_start(
            {"exec_id": exec_id, "start_container": True, "attach": False}
        )

        TestHelper.sleep(1)

        pruned_ids = TestHelper.container_prune()
        assert container1.id in pruned_ids
        assert container3.id in pruned_ids
        assert container2.id not in pruned_ids

        TestHelper.container_stop(container2.id)

    def test_inspect_a_container(self):
        container = TestHelper.container_successfully_create(
            {"name": "testcontainer"})

        response = TestHelper.container_inspect_raw("notexist")
        assert response.status == 404

        response = TestHelper.container_inspect_raw(container.name)
        assert response.status == 200

        result = TestHelper.decode_response_body(response.resp_body)
        assert result["container"]["name"] == container.name
        TestHelper.assert_schema(result, "ContainerInspect", )

    def test_start_and_stop_container_with_devfs(self):
        config = {"name": "testcont", "cmd": ["/bin/sleep", "10"]}
        container, exec_id = TestHelper.container_start_attached(config)

        assert TestHelper.devfs_mounted(container)
        TestHelper.container_stop(container.id)
        TestHelper.assert_container_shutdown(exec_id)

        assert not TestHelper.devfs_mounted(container)

    def test_start_container_without_attaching(self):
        container = TestHelper.container_successfully_create(
            {
                "name": "ws_test_container",
                "image": "FreeBSD:testing",
                "cmd": ["/bin/sh", "-c", "uname"],
            }
        )
        exec_id = TestHelper.exec_create(container.id)

        config = {"exec_id": exec_id, "attach": False, "start_container": True}
        TestHelper.exec_valid_start(config)
        TestHelper.sleep(0.1)

        TestHelper.container_remove(container.id)

    def test_start_container_with_attach_and_receive_output(self):
        cmd_expected = ["/bin/echo", "test test"]
        container = TestHelper.container_successfully_create(
            {"name": "testcont", "cmd": cmd_expected}
        )
        assert container.cmd == cmd_expected

        exec_id = TestHelper.exec_create(container.id)
        TestHelper.exec_start(
            exec_id, {"attach": True, "start_container": True})

        TestHelper.assert_received_output(exec_id, "test test\n")
        TestHelper.assert_container_shutdown(exec_id)
        assert not TestHelper.devfs_mounted(container)

    def test_start_and_force_stop_container(self):
        container = TestHelper.container_successfully_create(
            {"name": "testcont", "cmd": ["/bin/sleep", "10"]}
        )

        exec_id = TestHelper.exec_create(container.id)
        TestHelper.exec_start(
            exec_id, {"attach": False, "start_container": True})

        TestHelper.sleep(0.5)
        TestHelper.container_stop(container.id)
        assert not Utils.is_container_running(container.id)

    def test_start_and_stop_with_devfs_and_rc(self):
        config = {
            "name": "testcont",
            "cmd": ["/bin/sleep", "10"],
            "jail_param": ["mount.devfs", 'exec.stop="/bin/sh /etc/rc.shutdown"'],
            "user": "root",
        }
        container, exec_id = TestHelper.container_start_attached(config)

        assert TestHelper.devfs_mounted(container)
        TestHelper.container_stop(container.id)
        TestHelper.assert_container_shutdown(exec_id)
        assert not TestHelper.devfs_mounted(container)

    def test_mount_nullfs_into_container(self):
        mount_path = "/kleene_nullfs_testing"
        config_rw = {
            "name": "testcont",
            "cmd": ["/usr/bin/touch", f"{mount_path}/testing_mounts.txt"],
            "mounts": [{"type": "nullfs", "source": "/mnt", "destination": mount_path}],
            "user": "root",
        }
        container_id, _, process_output = TestHelper.container_valid_run(
            config_rw)
        assert process_output == []
        file_path = (
            f"/zroot/kleene/container/{container_id}/{mount_path}/testing_mounts.txt"
        )
        assert File.read(file_path) == {"error": "enoent"}
        assert File.read("/mnt/testing_mounts.txt") == {"ok": ""}

        config_ro = {
            "name": "testcont",
            "cmd": ["/usr/bin/touch", f"{mount_path}/testing_mounts.txt"],
            "mounts": [
                {
                    "type": "nullfs",
                    "source": "/mnt/",
                    "destination": mount_path,
                    "read_only": True,
                }
            ],
            "user": "root",
            "expected_exit_code": 1,
        }
        _, _, output = TestHelper.container_valid_run(config_ro)
        expected_output = (
            "touch: /kleene_nullfs_testing/testing_mounts.txt: Read-only file system\n"
            "jail: /usr/bin/env /usr/bin/touch /kleene_nullfs_testing/testing_mounts.txt: failed\n"
        )
        assert "".join(output) == expected_output

    def test_volume_mount_rw_permissions(self):
        volume = TestHelper.volume_create("volume-mounting-test")
        mount_path = "/kleene_volume_testing"

        config = {
            "name": "testcont",
            "cmd": ["/usr/bin/touch", f"{mount_path}/testing_mounts.txt"],
            "mounts": [
                {"type": "volume", "source": volume.name, "destination": mount_path}
            ],
            "user": "root",
        }

        container_id, _, process_output = TestHelper.container_valid_run(
            config)
        assert process_output == []
        file_path = (
            f"/zroot/kleene/container/{container_id}/{mount_path}/testing_mounts.txt"
        )
        assert File.read(file_path) == {"error": "enoent"}
        file_path = f"/zroot/kleene/volumes/{volume.name}/testing_mounts.txt"
        assert File.read(file_path) == {"ok": ""}
        TestHelper.volume_remove(volume.name)

    def test_volume_mount_read_only_permissions(self):
        volume = TestHelper.volume_create("volume-mounting-test")
        mount_path = "/kleene_volume_testing"

        config = {
            "name": "testcont",
            "cmd": ["/usr/bin/touch", f"{mount_path}/testing_mounts.txt"],
            "mounts": [
                {
                    "type": "volume",
                    "source": volume.name,
                    "destination": mount_path,
                    "read_only": True,
                }
            ],
            "user": "root",
            "expected_exit_code": 1,
        }

        _, _, output = TestHelper.container_valid_run(config)
        expected_output = (
            "touch: /kleene_volume_testing/testing_mounts.txt: Read-only file system\n"
            "jail: /usr/bin/env /usr/bin/touch /kleene_volume_testing/testing_mounts.txt: failed\n"
        )
        assert "".join(output) == expected_output

        TestHelper.volume_remove(volume.name)


class TestContainerVolumeManagement:

    def test_mount_empty_volume_into_non_empty_directory(self):
        volume = TestHelper.volume_create("volume-populate-test")
        mount_path = "/etc/defaults"

        config = {
            "name": "testcont",
            "cmd": ["/usr/bin/touch", f"{mount_path}/test_volume_mount"],
            "mounts": [
                {"type": "volume", "source": volume.name, "destination": mount_path}
            ],
            "user": "root",
        }

        container_id, _, process_output = TestHelper.container_valid_run(
            config)
        assert process_output == []

        output, exit_code = OS.cmd(["/bin/ls", volume.mountpoint])
        assert exit_code == 0
        assert (
            output
            == "bluetooth.device.conf\ndevfs.rules\nperiodic.conf\nrc.conf\ntest_volume_mount\n"
        )

        TestHelper.volume_remove(volume.name)

    def test_mount_non_existing_volume_into_container(self):
        mount_path = "/kleene_volume_testing"
        volume_name = "will-be-created"

        config = {
            "name": "testcont",
            "cmd": ["/usr/bin/touch", f"{mount_path}/testing_mounts.txt"],
            "mounts": [
                {"type": "volume", "source": volume_name, "destination": mount_path}
            ],
            "user": "root",
        }

        container_id, _, process_output = TestHelper.container_valid_run(
            config)
        assert process_output == []

        file_path = (
            f"/zroot/kleene/container/{container_id}/{mount_path}/testing_mounts.txt"
        )
        assert File.read(file_path) == {"error": "enoent"}

        file_path = f"/zroot/kleene/volumes/{volume_name}/testing_mounts.txt"
        assert File.read(file_path) == {"ok": ""}


class TestContainerUpdate:

    def test_updating_a_container(self):
        container = TestHelper.container_successfully_create(
            {
                "name": "testcontainer",
                "user": "ntpd",
                "cmd": ["/bin/sleep", "10"],
                "env": ["TESTVAR=testval"],
                "jail_param": ["allow.raw_sockets=true"],
            }
        )

        container_id = container.id
        config_nil = {
            "name": None,
            "user": None,
            "cmd": None,
            "env": None,
            "jail_param": None,
        }

        # Test a "nil-update"
        TestHelper.container_update(container_id, config_nil)
        container_upd = TestHelper.container_inspect(container_id)["container"]
        assert container_upd == container

        # Test changing name
        TestHelper.container_update(
            , container_id, {**config_nil, "name": "testcontupd"}
        )
        container_upd = TestHelper.container_inspect(container_id)["container"]
        assert container_upd["name"] == "testcontupd"

        # Test changing env and cmd
        TestHelper.container_update(
            ,
            container_id,
            {**config_nil, "env": ["TESTVAR=testval2"],
                "cmd": ["/bin/sleep", "20"]},
        )
        container_upd = TestHelper.container_inspect(container_id)["container"]
        assert container_upd["env"] == ["TESTVAR=testval2"]
        assert container_upd["cmd"] == ["/bin/sleep", "20"]

        # Test changing jail-param
        TestHelper.container_update(
            ,
            container_id,
            {**config_nil, "user": "root",
                "jail_param": ["allow.raw_sockets=false"]},
        )
        container_upd = TestHelper.container_inspect(container_id)["container"]
        assert container_upd["jail_param"] == ["allow.raw_sockets=false"]
        assert container_upd["user"] == "root"


class TestContainerAdvanced:

    def test_updating_on_a_running_container(self):
        container = TestHelper.container_successfully_create(
            {
                "name": "testcontainer",
                "user": "root",
                "cmd": ["/bin/sh", "/etc/rc"],
                "jail_param": ["mount.devfs"],
            }
        )

        container_id = container.id
        config_nil = {
            "name": None,
            "user": None,
            "cmd": None,
            "env": None,
            "jail_param": None,
        }

        # Start the container
        exec_id = TestHelper.exec_create(container_id)
        TestHelper.exec_valid_start(
            {"exec_id": exec_id, "start_container": True, "attach": True}
        )

        # Update jail-param
        TestHelper.container_update(
            ,
            container_id,
            {
                **config_nil,
                "jail_param": ["mount.devfs", "host.hostname=testing.local"],
            },
        )
        container_upd = TestHelper.container_inspect(container_id)["container"]
        assert container_upd["jail_param"] == [
            "mount.devfs",
            "host.hostname=testing.local",
        ]

        # Test hostname update
        exec_id = TestHelper.exec_create(
            {"container_id": container_id, "cmd": ["/bin/hostname"]}
        )
        _, output = TestHelper.exec_valid_start(
            {"exec_id": exec_id, "attach": True, "start_container": False}
        )
        assert output == ["testing.local\n"]

        # Test unsupported jail-param update
        with pytest.raises(Exception, match=r"vnet cannot be changed after creation"):
            TestHelper.container_update(
                , container_id, {**config_nil, "jail_param": ["vnet"]}
            )

        TestHelper.container_stop(container_id)

    def test_create_container_from_non_existing_image(self):
        with pytest.raises(Exception, match="no such image 'nonexisting'"):
            TestHelper.container_create(
                {"name": "testcont", "image": "nonexisting"})

    def test_start_a_container_as_non_root(self):
        container, exec_id = TestHelper.container_start_attached(
            , {"name": "testcont", "cmd": ["/usr/bin/id"], "user": "ntpd"}
        )

        assert TestHelper.assert_receive(
            {
                "container": exec_id,
                "output": "uid=123(ntpd) gid=123(ntpd) groups=123(ntpd)\n",
            }
        )
        TestHelper.assert_receive(
            {
                "container": exec_id,
                "shutdown": {"status": "jail_stopped", "exit_code": 0},
            }
        )

    def test_jail_parameters_replacement(self):
        # Override mount.devfs=true with mount.nodevfs
        config = {"jail_param": ["mount.nodevfs"],
                  "cmd": ["/bin/sh", "-c", "ls /dev"]}
        _, _, process_output = TestHelper.container_valid_run(config)
        assert process_output == []

        # Override mount.devfs=true/exec.clean=true with mount.devfs=false/exec.noclean
        config = {
            "jail_param": ["mount.devfs=false", "exec.noclean"],
            "cmd": ["/bin/sh", "-c", "ls /dev && printenv"],
        }
        _, _, output = TestHelper.container_valid_run(config)
        environment = TestHelper.from_environment_output(output)
        assert "EMU=beam" in environment

        # Override mount.devfs=true with itself
        config = {"jail_param": ["mount.devfs"],
                  "cmd": ["/bin/sh", "-c", "ls /dev"]}
        _, _, output = TestHelper.container_valid_run(config)
        assert output == [
            "fd\nnull\npts\nrandom\nstderr\nstdin\nstdout\nurandom\nzero\nzfs\n"
        ]

        # Override exec.clean=true with itself
        config = {
            "jail_param": ["exec.clean=true"],
            "cmd": ["/bin/sh", "-c", "printenv"],
        }
        _, _, output = TestHelper.container_valid_run(config)
        environment = TestHelper.from_environment_output(output)
        assert environment == TestHelper.jail_environment([])

    def test_jail_param_exec_jail_user_overrides_container_config_user(self):
        config = TestHelper.container_config(
            {
                "jail_param": ["exec.jail_user=ntpd"],
                "user": "root",
                "cmd": ["/usr/bin/id"],
            }
        )

        _, _, output = TestHelper.container_valid_run(config)
        assert output == ["uid=123(ntpd) gid=123(ntpd) groups=123(ntpd)\n"]

    def test_start_container_with_environment_variables_set(self):
        config = {
            "image": "FreeBSD:testing",
            "name": "testcont",
            "cmd": ["/bin/sh", "-c", "printenv"],
            "env": ["LOL=test", "LOOL=test2"],
            "user": "root",
            "attach": True,
        }

        _, _, output = TestHelper.container_valid_run(config)
        TestHelper.compare_environment_output(
            output, ["LOOL=test2", "LOL=test"])

    def test_start_container_with_environment_variables(self):
        dockerfile = """
        FROM FreeBSD:testing
        ENV TEST=lol
        ENV TEST2="lool test"
        CMD printenv
        """

        TestHelper.create_tmp_dockerfile(dockerfile, "tmp_dockerfile")
        image, _build_log = TestHelper.image_valid_build(
            {"context": "./", "dockerfile": "tmp_dockerfile", "tag": "test:latest"}
        )

        config = TestHelper.container_config(
            {"image": image.id, "env": ["TEST3=loool"]}
        )

        _, _, output = TestHelper.container_valid_run(config)
        TestHelper.compare_environment_output(
            output, ["TEST=lol", "TEST2=lool test", "TEST3=loool"]
        )

    def test_start_container_with_environment_variables_and_overwrite_one(self):
        dockerfile = """
        FROM FreeBSD:testing
        ENV TEST=lol
        ENV TEST2="lool test"
        CMD /bin/sh -c "printenv"
        """

        TestHelper.create_tmp_dockerfile(dockerfile, "tmp_dockerfile")
        image, _build_log = TestHelper.image_valid_build(
            {"context": "./", "dockerfile": "tmp_dockerfile", "tag": "test:latest"}
        )

        config = TestHelper.container_config(
            {"image": image.id, "env": ["TEST=new_value"]}
        )

        _, _, output = TestHelper.container_valid_run(config)
        TestHelper.compare_environment_output(
            output, ["TEST=new_value", "TEST2=lool test"]
        )

    def test_try_to_remove_a_running_container(self):
        config = {
            "name": "remove_while_running",
            "image": "FreeBSD:testing",
            "user": "root",
            "cmd": ["/bin/sh", "/etc/rc"],
            "attach": True,
        }

        container_id, _, _ = TestHelper.container_valid_run(config)

        with pytest.raises(Exception, match="you cannot remove a running container"):
            TestHelper.container_remove(container_id)

        TestHelper.container_stop(container_id)

    def test_try_to_remove_a_container_twice(self):
        config = {
            "name": "remove_while_running",
            "image": "FreeBSD:testing",
            "user": "root",
            "cmd": ["echo", "testing"],
            "attach": True,
        }

        container_id, _, _ = TestHelper.container_valid_run(config)
        removed_container = TestHelper.container_remove(container_id)
        assert removed_container["id"] == container_id

        with pytest.raises(Exception, match="no such container"):
            TestHelper.container_remove(container_id)

    def test_restart_on_startup_containers(self):
        TestHelper.network_create(
            {
                "name": "testnet",
                "subnet": "172.19.0.0/16",
                "gateway": "<auto>",
                "type": "bridge",
            }
        )

        config = TestHelper.container_config(
            {
                "name": "test-restart1",
                "jail_param": ["mount.nodevfs"],
                "cmd": ["/bin/sleep", "10"],
                "network_driver": "ipnet",
                "network": "testnet",
                "restart_policy": "on-startup",
            }
        )

        container1 = TestHelper.container_successfully_create(
            {**config, "name": "test-restart1", "network_driver": "ipnet"}
        )
        container2 = TestHelper.container_successfully_create(
            {**config, "name": "test-restart2", "network_driver": "vnet"}
        )

        Application.stop("kleened")
        assert OS.shell("ifconfig kleene0 destroy") == ("", 0)

        Application.start("kleened")
        TestHelper.sleep(0.2)

        assert TestHelper.container_inspect(
            container1.id)["container"]["running"]
        assert TestHelper.container_inspect(
            container2.id)["container"]["running"]

        assert OS.shell("ifconfig kleene0")[1] == 0

    def test_containers_with_persist_flag_not_pruned(self):
        container1 = TestHelper.container_successfully_create(
            {"name": "testprune1", "cmd": ["/bin/sleep", "10"]}
        )
        container2 = TestHelper.container_successfully_create(
            {"name": "testprune2", "cmd": [
                "/bin/sleep", "10"], "persist": True}
        )
        container3 = TestHelper.container_successfully_create(
            {"name": "testprune3", "cmd": ["/bin/sleep", "10"]}
        )

        pruned_containers = TestHelper.container_prune()
        assert container1.id in pruned_containers
        assert container3.id in pruned_containers
        assert container2.id not in pruned_containers

        remaining_containers = TestHelper.container_list()
        assert any(
            container["id"] == container2.id for container in remaining_containers
        )

        TestHelper.container_stop(container2.id)

    def test_start_container_repeatedly_for_reproducibility(self):
        container = TestHelper.container_successfully_create(
            {
                "name": "ws_test_container",
                "image": "FreeBSD:testing",
                "cmd": ["/bin/sh", "-c", "uname"],
            }
        )

        container_id = container.id
        assert (
            TestHelper.start_n_attached_containers_and_receive_output(
                container_id, 20)
            == "ok"
        )
        assert TestHelper.container_remove(container_id)["id"] == container_id
