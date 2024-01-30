import os
import subprocess

from testutils import (
    create_dockerfile,
    build_image,
    decode_valid_image_build,
    decode_invalid_image_build,
    create_image,
    remove_all_containers,
    remove_all_images,
    remove_image,
    inspect,
    prune,
    run,
)

from klee.utils import human_duration


class TestImageSubcommand:
    # pylint: disable=no-self-use
    instructions = [
        "FROM FreeBSD:testing",
        'RUN echo "lol" > /root/test.txt',
        "CMD /usr/bin/uname",
    ]

    @classmethod
    def setup_class(cls):
        remove_all_containers()
        remove_all_images()

    def test_empty_listing_of_images(self):
        assert_empty_image_list()

    def test_build_remove_and_list_images(self):
        create_dockerfile(self.instructions)
        result = build_image()
        image_id, _build_log = decode_valid_image_build(result)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)
        assert_empty_image_list()

    def test_inspect_image(self):
        create_dockerfile(self.instructions)
        result = build_image()
        image_id, _build_log = decode_valid_image_build(result)
        assert inspect("image", "notexist") == "image not found"
        image_endpoints = inspect("image", image_id)
        assert image_endpoints["id"] == image_id
        remove_image(image_id)

    def test_prune_image(self):
        create_dockerfile(self.instructions)
        result = build_image()
        image_id1, _build_log = decode_valid_image_build(result)

        create_dockerfile(self.instructions)
        result = build_image()
        image_id2, _build_log = decode_valid_image_build(result)
        assert prune("image") == [image_id2, image_id1]

    def test_update_tag(self):
        create_dockerfile(self.instructions)
        result = build_image(tag="test:re-tagging")
        image_id, _build_log = decode_valid_image_build(result)
        output = run(f"image tag {image_id} test2:newtag")
        assert output[0] == image_id
        image_endpoints = inspect("image", image_id)
        assert image_endpoints["name"] == "test2"
        assert image_endpoints["tag"] == "newtag"
        remove_image(image_id)

    def test_build_image_receive_build_messages(self):
        create_dockerfile(self.instructions)
        result = build_image(quiet=False)
        image_id, build_log = decode_valid_image_build(result)
        expected_log = [
            "Step 1/3 : FROM FreeBSD:testing",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "--> Snapshot created: @",
            "Step 3/3 : CMD /usr/bin/uname",
            "",
        ]
        verify_build_output(expected_log, build_log)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)
        assert_empty_image_list()

    def test_build_and_remove_and_with_a_tag(self):
        create_dockerfile(self.instructions)
        result = build_image(tag="testlol:testest")
        image_id, _build_log = decode_valid_image_build(result)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert (
            list_images()[0]
            == f" {image_id}   testlol   testest   Less than a second ago "
        )
        assert succesfully_remove_image(image_id)
        assert_empty_image_list()

    def test_build_image_with_buildarg(self):
        instructions = ["FROM FreeBSD:testing", "ARG TEST=notthis", 'RUN echo "$TEST"']
        create_dockerfile(instructions)
        result = build_image(quiet=False, buildargs={"TEST": "but_this"})
        image_id, build_log = decode_valid_image_build(result)
        expected_log = [
            "Step 1/3 : FROM FreeBSD:testing",
            "Step 2/3 : ARG TEST=notthis",
            'Step 3/3 : RUN echo "$TEST"',
            "but_this",
            "--> Snapshot created: @",
        ]
        verify_build_output(expected_log, build_log)
        assert succesfully_remove_image(image_id)

    def test_failed_build_without_cleanup(self):
        instructions = [
            "FROM FreeBSD:testing",
            'RUN echo "lol" > /root/test.txt',
            "RUN ls notexist",
        ]
        create_dockerfile(instructions)
        result = build_image(quiet=False, cleanup=False)
        image_id, build_log = decode_invalid_image_build(result)
        expected_build_log = [
            "Step 1/3 : FROM FreeBSD:testing",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "--> Snapshot created: @",
            "Step 3/3 : RUN ls notexist",
            "ls: notexist: No such file or directory",
            "jail: /usr/bin/env /bin/sh -c ls notexist: failed",
            "The command '/bin/sh -c ls notexist' returned a non-zero code: 1",
        ]

        verify_build_output(expected_build_log, build_log)
        output = run(f"run {image_id} /bin/cat /root/test.txt", exit_code=0)

        prefix = "created execution instance "
        assert output[1][: len(prefix)] == prefix
        assert output[2] == "lol"

    def test_inspect_snapshot_in_failed_build(self):
        instructions = [
            "FROM FreeBSD:testing",
            'RUN echo "first" > /root/test.txt',
            "RUN ls notexist",
        ]
        create_dockerfile(instructions)
        result = build_image(quiet=False, cleanup=False)
        image_id, build_log = decode_invalid_image_build(result)
        expected_build_log = [
            # f"Started to build image with ID {image_id}",
            "Step 1/3 : FROM FreeBSD:testing",
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

    def test_invalid_dockerfile(self):
        instructions = [
            "ENV testvar=lol",
            "FROM FreeBSD:testing",
            'RUN echo "this never happens"',
        ]
        create_dockerfile(instructions)
        result = build_image(quiet=False)
        assert result == [
            "error in 'ENV testvar=lol': instruction not permitted before a FROM instruction",
            "",
        ]


class TestImageCreateSubcommand:
    @classmethod
    def setup_class(cls):
        remove_all_containers()
        remove_all_images()

    def test_create_image_with_fetch_method(self):
        url = "file:///home/vagrant/kleened/test/data/minimal_testjail.txz"
        result = create_image("fetch", tag="ImageCreate:test", url=url)
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert resolv_conf_exist(image_id)
        assert succesfully_remove_image(image_id)

    def test_create_image_with_fetch_method_and_nodns(self):
        url = "file:///home/vagrant/kleened/test/data/minimal_testjail.txz"
        result = create_image("fetch", tag="ImageCreate:test-nodns", dns=False, url=url)
        assert result[-3] == "image created"
        image_id = result[-2]

        assert not resolv_conf_exist(image_id)
        assert succesfully_remove_image(image_id)

    def test_create_image_with_zfs_method(self):
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
        result = create_image("zfs-copy", tag="ImageCreate:test-zfs", dataset=dataset)
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert resolv_conf_exist(image_id)
        assert succesfully_remove_image(image_id)

    def test_create_image_with_zfs_method_nodns(self):
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
        result = create_image(
            "zfs-copy", tag="ImageCreate:test-zfs", dns=False, dataset=dataset
        )
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert not resolv_conf_exist(image_id)
        assert succesfully_remove_image(image_id)


def resolv_conf_exist(image_id):
    resolv_conf = f"/zroot/kleene/image/{image_id}/etc/resolv.conf"
    return os.path.isfile(resolv_conf)


def verify_build_output(expected_log, build_log):
    for expected, log in zip(expected_log, build_log):
        assert log[: len(expected)] == expected


def succesfully_remove_image(image_id):
    output = remove_image(image_id)
    return output[0] == image_id


def list_images():
    _, _, *images = run("image ls")
    return images


def image_id_from_list(index):
    images = list_images()
    image_id = images[index][1:13]
    return image_id


def assert_empty_image_list():
    created = human_duration("2023-09-14T21:21:57.990515Z")
    output = run("image ls")
    assert output[:2] == [
        " ID             NAME      TAG       CREATED      ",
        "─────────────────────────────────────────────────",
    ]

    assert output[2][13:] == f"   FreeBSD   testing   {created} ago "
