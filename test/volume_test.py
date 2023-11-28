from testutils import (
    create_container,
    create_dockerfile,
    build_image,
    decode_valid_image_build,
    extract_exec_id,
    remove_all_containers,
    remove_container,
    remove_image,
    inspect,
    prune,
    run,
    container_stopped_msg,
)


class TestVolumeSubcommand:
    instructions = [
        "FROM FreeBSD:testing",
        "RUN mkdir /testdir1",
        "RUN mkdir /testdir2",
    ]

    # pylint: disable=no-self-use
    @classmethod
    def setup_class(cls):
        remove_all_containers()
        remove_all_volumes()

    def test_add_remove_and_listing_volumes(self):
        name = "test_arl_volumes"
        assert empty_volume_list()
        assert name == create_volume(name)
        assert [name] == list_volumes()
        assert name == remove_volume(name)
        assert empty_volume_list()

    def test_inspect_volume(self):
        name = "test_volume_inspect"
        volume_name = create_volume(name=name)
        assert inspect("volume", "notexist") == "No such volume"
        volume_mountpoints = inspect("volume", volume_name)
        assert volume_mountpoints["volume"]["name"] == name
        remove_volume(volume_name)

    def test_prune_volume(self):
        name1 = "test_volume_prune1"
        name2 = "test_volume_prune2"
        create_volume(name=name1)
        create_volume(name=name2)
        assert prune("volume") == [name1, name2]

    def test_creating_a_container_with_writable_volume(self):
        volume_name = "cont_rw_vol1"
        image_name = "img_volrw:latest"

        create_volume(volume_name)
        create_dockerfile(self.instructions)
        result = build_image(tag=image_name)
        image_id, _ = decode_valid_image_build(result)
        container_id = create_container(
            name="test_cont_rw_vol",
            volumes=["cont_rw_vol1:/testdir1", "/testdir2"],
            image=image_name,
            command="/usr/bin/touch /testdir1/testfile",
        )
        output = run(f"container start --attach {container_id}")
        exec_id = extract_exec_id(output)
        expected_output = [
            f"created execution instance {exec_id}",
            "",
            container_stopped_msg(exec_id),
            "",
        ]
        assert output == expected_output
        assert len(list_volumes()) == 2
        remove_all_volumes()
        remove_container(container_id)
        remove_image(image_id)

    def test_creating_a_container_with_readonly_volume(self):
        volume_name = "cont_ro_vol1"
        image_name = "img_volro:latest"

        create_volume(volume_name)
        create_dockerfile(self.instructions)
        result = build_image(tag=image_name)
        image_id, _ = decode_valid_image_build(result)
        container_id = create_container(
            name="test_cont_ro_vol",
            volumes=[f"{volume_name}:/testdir1:ro", "/testdir2:ro"],
            image=image_name,
            command="/usr/bin/touch /testdir1/testfile",
        )
        output = run(f"container start --attach {container_id}")

        exec_id = extract_exec_id(output)
        expected_output = [
            f"created execution instance {exec_id}",
            "touch: /testdir1/testfile: Read-only file system",
            "jail: /usr/bin/env /usr/bin/touch /testdir1/testfile: failed",
        ]

        assert output[:3] == expected_output
        assert len(list_volumes()) == 2
        remove_all_volumes()
        remove_container(container_id)
        remove_image(image_id)


def create_volume(name):
    output = run(f"volume create {name}")
    return output[0]


def empty_volume_list():
    expected_output = [" VOLUME NAME   CREATED ", "───────────────────────", ""]
    output = run("volume ls")
    return expected_output == output


def remove_volume(volume_name):
    output = run(f"volume rm {volume_name}")
    network_id = output[0]
    return network_id


def list_volumes():
    output = run("volume ls")
    _header, _headerline, *volumes, _ = output
    volumes = [volume.split(" ")[1] for volume in volumes]
    return volumes


def remove_all_volumes():
    volumes = list_volumes()
    if len(volumes) > 0:
        volumes = " ".join(volumes)
        run(f"volume rm {volumes}")
