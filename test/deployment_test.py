from testutils import run, create_dockerfile, create_deployment_file, inspect, shell, listing_ids

# pylint: disable=unused-argument


class TestDeployBuild:

    def test_create_a_base_image(self, cleanup_all):
        deployment = """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"
"""
        create_deployment_file(deployment)
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."

    def test_create_twice_a_base_image(self, cleanup_all):
        deployment = """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"
"""
        create_deployment_file(deployment)
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."

    instructions = [
        "FROM FreeBSD",
        'RUN echo "lol" > /root/test.txt',
        "CMD /usr/bin/uname",
    ]

    def test_build_error_when_using_method_and_context_simultaneously(
        self, cleanup_all
    ):
        deployment = """
---
images:
  - tag: "bsdtest2"
    method: "zfs-clone"
    context: "bsdtest2"
"""
        create_deployment_file(deployment)
        output = run("deploy build", exit_code=1)
        output = "".join(output)
        error = "error in image bsdtest2: both 'context' and 'method' cannot be specified at the same time."
        assert output == error

    def test_build_error_when_trying_to_build_image_from_nonexisting_parent(
        self, cleanup_all
    ):
        instructions = [
            'RUN echo "lol" > /root/test.txt',
            "CMD /usr/bin/uname",
        ]
        deployment = """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

  - tag: "bsdtest2"
    context: "bsdtest2"
"""
        create_deployment_file(deployment)
        create_dockerfile(instructions, parent="nonexisting", path="bsdtest2")
        output = run("deploy build", exit_code=1)
        assert output[0] == "Start building images.."
        assert (
            output[1]
            == "image build list contains images with a non-existing parent image"
        )
        assert output[-2] == "Failed to build deployment"

    def test_build_an_image_from_a_base_image(self, cleanup_all):
        instructions = [
            'RUN echo "lol" > /root/test.txt',
            "CMD /usr/bin/uname",
        ]
        deployment = """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

  - tag: "bsdtest2"
    context: "bsdtest2"
"""
        create_deployment_file(deployment)
        create_dockerfile(instructions, parent="bsdtest", path="bsdtest2")
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."

    def test_build_an_image_with_a_custom_container_config(self, cleanup_all):
        instructions = [
            "RUN echo $TESTING",
            "RUN id",
            "CMD /usr/bin/uname",
        ]
        deployment = """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

  - tag: "bsdtest2"
    context: "bsdtest2"
    container_config:
      user: ntpd
      env:
        - "LOL=testing"
        - "TESTING=lol"
"""
        create_deployment_file(deployment)
        create_dockerfile(instructions, parent="bsdtest", path="bsdtest2")
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."
        assert "lol\n" in "\n".join(output)
        assert "(ntpd)\n" in "\n".join(output)

    def test_build_a_parent_and_a_child_image(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

  - tag: "bsdtest2"
    context: "bsdtest2"

  - tag: "bsdtest3"
    context: "bsdtest2"
"""
        )
        instructions = [
            'RUN echo "lol" > /root/test.txt',
            "CMD /usr/bin/uname",
        ]
        create_dockerfile(instructions, parent="bsdtest", path="bsdtest2")
        create_dockerfile(instructions, parent="bsdtest2", path="bsdtest3")
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."

    def test_build_two_images_from_a_base_image(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

  - tag: "bsdtest2"
    context: "bsdtest2"

  - tag: "bsdtest3"
    context: "bsdtest2"
"""
        )
        instructions = [
            'RUN echo "lol" > /root/test.txt',
            "CMD /usr/bin/uname",
        ]
        create_dockerfile(instructions, parent="bsdtest", path="bsdtest2")
        create_dockerfile(instructions, parent="bsdtest", path="bsdtest3")
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."

    def test_build_images_with_pre_existing_parents(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "bsdtest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

  - tag: "bsdtest2"
    context: "bsdtest2"

  - tag: "bsdtest3"
    context: "bsdtest2"
"""
        )
        instructions = [
            'RUN echo "lol" > /root/test.txt',
            "CMD /usr/bin/uname",
        ]
        output = run("image create -t bsdtest0 zfs-clone zroot/kleene_basejail")
        create_dockerfile(instructions, parent="bsdtest", path="bsdtest2")
        create_dockerfile(instructions, parent="bsdtest0", path="bsdtest3")
        output = run("deploy build")
        assert output[0] == "Start building images.."
        assert output[-2] == "Succesfully built images."


class TestDeployCreateAndRemove:

    def test_create_and_remove_a_single_container(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

containers:
 - name: "test1"
   image: "FreeBSD:latest"
"""
        )
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        output = run("deploy create")
        assert output[0][:25] == "created container 'test1'"
        container_id = output[0].split(": ")[1]
        output = run("deploy remove -F")
        assert output[1] == container_id

    def test_create_and_remove_two_containers(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

containers:
 - name: "test1"
   image: "FreeBSD:latest"

 - name: "test2"
   image: "FreeBSD:latest"
"""
        )
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        output = run("deploy create")
        assert output[0][:25] == "created container 'test1'"
        assert output[1][:25] == "created container 'test2'"
        container_id1 = output[0].split(": ")[1]
        container_id2 = output[1].split(": ")[1]
        output = run("deploy remove -F")
        assert output[1] == container_id1
        assert output[2] == container_id2

    def test_creating_containers_is_idempotent(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

containers:
 - name: "testcon1"
   image: "FreeBSD:latest"
"""
        )
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        output = run("deploy create")
        assert output[0].split(":")[0] == "created container 'testcon1'"
        output = run("deploy create")
        assert output == [""]

    def test_creating_container_when_its_image_has_not_been_created(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

containers:
 - name: "testcon1"
   image: "FreeBSD:latest"
"""
        )
        output = run("deploy create")
        assert (
            output[0]
            == "could not create container 'testcon1': no such image 'FreeBSD:latest'"
        )

    def test_create_and_remove_a_network(self, cleanup_all):
        create_deployment_file(
            """
---
networks:
  - name: "testnet"
    subnet: "10.13.37.0/24"
    type: "loopback"
"""
        )
        output = run("deploy create")
        assert output[0] == "created network 'testnet'"
        network = inspect("network", "testnet")["network"]["id"]
        output = run("deploy remove -F")
        assert output[2] == network

    def test_creating_networks_is_idempotent(self, cleanup_all):
        create_deployment_file(
            """
---
networks:
  - name: "testnet"
    subnet: "10.13.37.0/24"
    type: "loopback"
"""
        )
        run("deploy create")
        output = run("deploy create")
        assert output == [""]

    def test_create_and_remove_a_volume(self, cleanup_all):
        create_deployment_file(
            """
---
volumes:
  - name: "teststorage"
"""
        )
        output = run("deploy create")
        assert output[0] == "created volume 'teststorage'"
        volume = inspect("volume", "teststorage")["volume"]["name"]
        # Test that no volumes is removed when '-v' is omitted:
        assert run("deploy remove -F") == [
            "Removing containers...",
            "Removing networks...",
            "",
        ]
        output = run("deploy remove -F -v")
        assert output[3] == volume

    def test_creating_volumes_is_idempotent(self, cleanup_all):
        create_deployment_file(
            """
---
volumes:
  - name: "teststorage"
"""
        )
        run("deploy create")
        output = run("deploy create")
        assert output[0] == ""

    def test_create_and_remove_a_container_with_volume_and_network(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

networks:
  - name: "testnet"
    type: "bridge"
    subnet: "10.13.37.0/24"

volumes:
  - name: "database-storage"

containers:
 - name: "dbcon"
   image: "FreeBSD:latest"
   endpoints:
     - network: "testnet"
   mounts:
     - type: "volume"
       source: "database-storage"
       destination: "/mnt/db"
"""
        )
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        output = run("deploy create")
        assert output[0] == "created network 'testnet'"
        assert output[1] == "created volume 'database-storage'"
        assert output[2].startswith("created container 'dbcon'")
        container_id = output[2].split(": ")[1]

        # The container is connected to the deployment network with an
        # allocated ip from its subnet:
        network = inspect("network", "testnet")["network"]
        assert network["name"] == "testnet"
        assert network["subnet"] == "10.13.37.0/24"
        endpoints = inspect("container", container_id)["container_endpoints"]
        assert len(endpoints) == 1
        assert endpoints[0]["network_id"] == network["id"]
        assert endpoints[0]["ip_address"].startswith("10.13.37.")

        # ... and the volume is mounted at the specified destination:
        mounts = inspect("container", container_id)["container_mountpoints"]
        assert any(
            m["type"] == "volume"
            and m["source"] == "database-storage"
            and m["destination"] == "/mnt/db"
            for m in mounts
        )

        output = run("deploy remove -F")
        assert container_id in output
        # The network was removed along with the deployment:
        assert "testnet" not in run("network ls")


def _is_running(container_id):
    """Whether the container is running, per jls."""
    output = shell("jls -j " + container_id)
    return "no such jail" not in output


class TestDeployLifecycle:
    def test_deploy_up_down_and_restart(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

containers:
 - name: "updown"
   image: "FreeBSD:latest"
   cmd: ["/bin/sleep", "100"]
"""
        )
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        output = run("deploy up")
        assert output[0] == "created container 'updown': " + output[0].split(": ")[1]
        container_id = output[0].split(": ")[1]

        # 'up' starts the containers it created:
        assert _is_running(container_id)

        # 'restart' stops and starts them again:
        run("deploy restart")
        assert _is_running(container_id)

        # 'down' stops and removes everything:
        run("deploy down")
        assert listing_ids(run("container ls -a")) == []

    def test_deploy_prune_removes_objects_outside_the_deployment(self, cleanup_all):
        create_deployment_file(
            """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"

containers:
 - name: "inspec"
   image: "FreeBSD:latest"
"""
        )
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        run("deploy create")

        # An orphan exists outside the deployment file:
        run("network create -t loopback --subnet 10.45.45.0/24 orphannet")
        run("volume create orphanvol")
        run("container create --name orphancon FreeBSD:latest")

        output = run("deploy prune")
        joined = " ".join(output)
        assert "removed container 'orphancon'" in joined
        assert "removed network 'orphannet'" in joined
        assert "removed volume 'orphanvol'" in joined

        # ... while the deployment's own objects are untouched:
        assert "inspec" in " ".join(run("container ls -a"))
        assert "testnet" not in " ".join(run("network ls"))
