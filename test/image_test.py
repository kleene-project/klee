import os
import subprocess

from testutils import (
    create_dockerfile,
    build_image,
    decode_valid_image_build,
    decode_invalid_image_build,
    list_images,
    stat,
    inspect,
    prune,
    run,
)

# pylint: disable=no-self-use, unused-argument
instructions = ["FROM FreeBSD", 'RUN echo "lol" > /root/test.txt', "CMD /usr/bin/uname"]

cwd = os.getcwd()


class TestImageSubcommand:
    def test_empty_listing_of_images(self, testimage):
        assert_only_test_image()

    def test_build_remove_and_list_images(self, testimage):
        create_dockerfile(instructions)
        result = build_image()
        image_id, _build_log = decode_valid_image_build(result)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        run(f"rmi {image_id}")
        assert_only_test_image()

    def test_inspect_image(self, testimage):
        create_dockerfile(instructions)
        result = build_image()
        image_id, _build_log = decode_valid_image_build(result)
        assert inspect("image", "notexist") == "image not found"
        image_endpoints = inspect("image", image_id)
        assert image_endpoints["id"] == image_id
        run(f"rmi {image_id}")

    def test_update_tag(self, testimage):
        create_dockerfile(instructions)
        result = build_image(tag="test:re-tagging")
        image_id, _build_log = decode_valid_image_build(result)
        output = run(f"image tag {image_id} test2:newtag")
        assert output[0] == image_id
        image_endpoints = inspect("image", image_id)
        assert image_endpoints["name"] == "test2"
        assert image_endpoints["tag"] == "newtag"
        run(f"rmi {image_id}")

    def test_build_image_receive_build_messages(self, testimage):
        create_dockerfile(instructions)
        result = build_image(quiet=False)
        image_id, build_log = decode_valid_image_build(result)
        expected_log = [
            "Step 1/3 : FROM FreeBSD",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "--> Snapshot created: @",
            "Step 3/3 : CMD /usr/bin/uname",
            "",
        ]
        verify_build_output(expected_log, build_log)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        run(f"rmi {image_id}")
        assert_only_test_image()

    def test_build_and_remove_and_with_a_tag(self, testimage):
        create_dockerfile(instructions)
        result = build_image(tag="testlol:testest")
        image_id, _build_log = decode_valid_image_build(result)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert (
            run("lsi")[2]
            == f" {image_id}   testlol   testest   Less than a second ago "
        )
        run(f"rmi {image_id}")
        assert_only_test_image()

    def test_build_image_with_buildarg(self, testimage):
        instructions = ["FROM FreeBSD", "ARG TEST=notthis", 'RUN echo "$TEST"']
        create_dockerfile(instructions)
        result = build_image(quiet=False, buildargs={"TEST": "but_this"})
        image_id, build_log = decode_valid_image_build(result)
        expected_log = [
            "Step 1/3 : FROM FreeBSD",
            "Step 2/3 : ARG TEST=notthis",
            'Step 3/3 : RUN echo "$TEST"',
            "but_this",
            "--> Snapshot created: @",
        ]
        verify_build_output(expected_log, build_log)
        run(f"rmi {image_id}")

    def test_build_using_dockerfile_containing_a_line_with_only_a_space(
        self, testimage
    ):
        create_dockerfile(["FROM FreeBSD", " ", "RUN touch /passed"])
        run(f"build -t StrangeDockerfile {os.getcwd()}")
        output = run(f"run --name testing1 StrangeDockerfile {stat('/passed')}")
        stat_output = output[2].split(",")
        file_permissions = stat_output[-1]
        assert "-rw-r--r--" == file_permissions
        run("rmc testing1")
        run("rmi StrangeDockerfile")

    def test_build_invalid_instruction(self, testimage):
        create_dockerfile(["FRO FreeBSD", "RUN echo 'doest not run'"])
        output = run(f"build -t InvalidDockerfile {os.getcwd()}", exit_code=1)
        assert ["error in 'FRO FreeBSD': invalid instruction", ""] == output

    def test_build_image_from_snapshot(self, testimage):
        dockerfile = dockerfile_from_str(
            """
           FROM FreeBSD
           RUN touch /media/step1
           RUN touch /media/step2
           """
        )
        create_dockerfile(dockerfile)
        run(f"build -t WithSnapshots {os.getcwd()}")

        image = inspect("image", "WithSnapshots")
        instruction, snapshot = image["instructions"][1]
        assert instruction == "RUN touch /media/step1"

        for n, nametag in enumerate(
            ["WithSnapshots", "WithSnapshots:latest", image["id"]]
        ):
            print("using namtag: ", nametag)
            dockerfile = dockerfile_from_str(
                f"""
               FROM {nametag}{snapshot}
               RUN echo "testing"
               """
            )
            create_dockerfile(dockerfile)
            run(f"build -t FromSnapshot{n} {os.getcwd()}")
            output = set(run(f"run FromSnapshot{n} ls /media"))
            assert "step1" in output
            assert "step2" not in output
        run("container prune -f")
        run("rmi FromSnapshot0 FromSnapshot1 FromSnapshot2 WithSnapshots")

    def test_failed_build_without_cleanup(self, testimage):
        instructions = [
            "FROM FreeBSD",
            'RUN echo "lol" > /root/test.txt',
            "RUN ls notexist",
        ]
        create_dockerfile(instructions)
        result = run(f"build -t FailedBuild:WithoutCleanup {os.getcwd()}", exit_code=1)
        image_id, build_log = decode_invalid_image_build(result)
        expected_build_log = [
            "Step 1/3 : FROM FreeBSD",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "--> Snapshot created: @",
            "Step 3/3 : RUN ls notexist",
            "ls: notexist: No such file or directory",
            "jail: /usr/bin/env /bin/sh -c ls notexist: failed",
            "The command '/bin/sh -c ls notexist' returned a non-zero code: 1",
        ]

        verify_build_output(expected_build_log, build_log)
        output = run(f"run {image_id} /bin/cat /root/test.txt")

        prefix = "created execution instance "
        assert output[1][: len(prefix)] == prefix
        assert output[2] == "lol"
        run("container prune -f")
        run(f"rmi {image_id}")

    def test_inspect_snapshot_in_failed_build(self, testimage):
        instructions = [
            "FROM FreeBSD",
            'RUN echo "first" > /root/test.txt',
            "RUN ls notexist",
        ]
        create_dockerfile(instructions)
        result = run(f"build -t FailedBuild:InspectSnapshot {os.getcwd()}", exit_code=1)
        image_id, build_log = decode_invalid_image_build(result)
        expected_build_log = [
            # "Started to build image with ID {image_id}",
            "Step 1/3 : FROM FreeBSD",
            'Step 2/3 : RUN echo "first" > /root/test.txt',
            "--> Snapshot created: @",
            "Step 3/3 : RUN ls notexist",
            "ls: notexist: No such file or directory",
            "jail: /usr/bin/env /bin/sh -c ls notexist: failed",
            "The command '/bin/sh -c ls notexist' returned a non-zero code: 1",
        ]

        snapshot_line = build_log[2]
        snapshot = snapshot_line.split("--> Snapshot created: @")[1]
        verify_build_output(expected_build_log, build_log)
        output = run(f"run {image_id}@{snapshot} /bin/cat /root/test.txt", exit_code=0)

        prefix = "created execution instance "
        assert output[1][: len(prefix)] == prefix
        assert output[2] == "first"
        run("container prune -f")
        run("rmi FailedBuild:failed")

    def test_invalid_dockerfile(self):
        instructions = [
            "ENV testvar=lol",
            "FROM FreeBSD",
            'RUN echo "this never happens"',
        ]
        create_dockerfile(instructions)
        result = run(f"build -t Invalid:Dockerfile {os.getcwd()}", exit_code=1)
        assert result == [
            "'ENV testvar=lol' not permitted before a FROM instruction",
            "",
        ]


class TestImageCreateSubcommand:
    def test_create_image_with_fetch_method(self, testimage):
        url = "file:///home/vagrant/kleened/test/data/minimal_testjail.txz"
        result = run(f"image create -t Create:Fetch fetch {url}")
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert resolv_conf_exist(image_id)
        run(f"rmi {image_id}")

    def test_create_image_with_fetch_method_and_nodns(self, testimage):
        url = "file:///home/vagrant/kleened/test/data/minimal_testjail.txz"
        result = run(f"image create --no-dns -t Create:Fetch-nodns fetch {url}")
        assert result[-3] == "image created"
        image_id = result[-2]

        assert not resolv_conf_exist(image_id)
        run(f"rmi {image_id}")

    def test_create_image_with_zfs_method(self, testimage):
        dataset = "zroot/kleene_testdataset"
        if os.path.isdir(f"/{dataset}"):
            subprocess.run(["/sbin/zfs", "destroy", "-rf", dataset], check=True)

        subprocess.run(["/sbin/zfs", "create", dataset], check=True)

        result = subprocess.run(
            [
                "/usr/bin/tar",
                "-xf",
                "/home/vagrant/kleened/test/data/minimal_testjail.txz",
                "-C",
                f"/{dataset}",
            ],
            check=True,
        )
        assert result.returncode == 0
        result = run(f"image create -t Create:ZFSCopy zfs-copy {dataset}")
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert resolv_conf_exist(image_id)
        run(f"rmi {image_id}")

    def test_create_image_with_zfs_method_nodns(self, testimage):
        dataset = "zroot/kleene_testdataset"
        if os.path.isdir(f"/{dataset}"):
            subprocess.run(["/sbin/zfs", "destroy", "-rf", dataset], check=True)

        subprocess.run(["/sbin/zfs", "create", dataset], check=True)

        result = subprocess.run(
            [
                "/usr/bin/tar",
                "-xf",
                "/home/vagrant/kleened/test/data/minimal_testjail.txz",
                "-C",
                f"/{dataset}",
            ],
            check=True,
        )
        assert result.returncode == 0
        result = run(
            f"image create --no-dns -t Create:ZFSCopy-nodns zfs-copy {dataset}"
        )
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert not resolv_conf_exist(image_id)
        run(f"rmi {image_id}")

    def test_create_image_with_zfs_invalid_image(self, testimage):
        result = run(
            "image create -t Create:ZFSClone-invalid zfs-clone /zroot/kleene_basejail/"
        )
        assert result == [
            "invalid dataset",
            "image creation failed: invalid dataset",
            "",
        ]


class TestImagePruning:
    def test_pruning_snapshot_image(self, host_state):
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        self.image("FreeBSD", "Parent")
        self.image_fail("Parent", "Parent:not_happening")
        image = inspect("image", "Parent:failed")
        _instruction, snapshot = image["instructions"][1]
        self.image(f"Parent:failed{snapshot}")

        images = {image.id for image in list_images()}
        assert set(prune("image", all_=True)) == images

    def image(self, parent, nametag=None):
        create_dockerfile([f"FROM {parent}", 'RUN echo "hello" > /world.txt'])
        if nametag is None:
            return run(f"image build {cwd}")

        return run(f"image build -t {nametag} {cwd}")

    def image_fail(self, parent, nametag=None):
        create_dockerfile([f"FROM {parent}", 'RUN echo "testing"', "RUN ls notexists"])
        if nametag is None:
            return run(f"image build {cwd}", exit_code=1)

        return run(f"image build -t {nametag} {cwd}", exit_code=1)


def dockerfile_from_str(dockerfile):
    return [line.strip() for line in dockerfile.split("\n")]


def resolv_conf_exist(image_id):
    resolv_conf = f"/zroot/kleene/image/{image_id}/etc/resolv.conf"
    return os.path.isfile(resolv_conf)


def verify_build_output(expected_log, build_log):
    for expected, log in zip(expected_log, build_log):
        assert log[: len(expected)] == expected


def image_id_from_list(index):
    images = list_images()
    return images[index].id


def assert_only_test_image():
    images = list_images()
    assert len(images) == 1
    assert images[0].name == "FreeBSD"
    assert images[0].tag == "latest"
