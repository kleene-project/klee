from testutils import run, create_dockerfile, create_deployment_file

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


class TestDeployCreate:

    def test_create_a_single_container(self, cleanup_all):
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

    def test_create_two_containers(self, cleanup_all):
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
        assert output[0] == "no such image 'FreeBSD:latest'"

    def test_create_a_network(self, cleanup_all):
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

    def test_create_a_volume(self, cleanup_all):
        create_deployment_file(
            """
---
volumes:
  - name: "teststorage"
"""
        )
        output = run("deploy create")
        assert output[0] == "created volume 'teststorage'"

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


class TestDeployRemove:

    def test_remove_a_single_container(self, cleanup_all):
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
        output = run("deploy remove -f")
        assert output[1] == container_id
