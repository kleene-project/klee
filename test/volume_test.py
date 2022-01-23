from testutils import create_container, remove_all_containers, remove_container, run, create_dockerfile, create_image, remove_image



class TestVolumeSubcommand:
    instructions = [
        "FROM scratch",
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
        assert [name, ""] == create_volume(name)
        assert [name] == list_volumes()
        assert name == remove_volume(name)
        assert empty_volume_list()

    def test_creating_a_container_with_writable_volume(self):
        volume_name = "cont_rw_vol1"
        image_name = "img_volrw:latest"

        create_volume(volume_name)
        create_dockerfile(self.instructions)
        image_id = create_image(tag=image_name)
        container_id = create_container(
            name="test_cont_rw_vol",
            volumes=["cont_rw_vol1:/testdir1", "/testdir2"],
            image=image_name,
            command="/usr/bin/touch /testdir1/testfile",
        )
        expected_output = [f'exit:container {container_id} stopped', '']
        assert run(f"container start --attach {container_id}") == expected_output
        assert len(list_volumes()) == 2
        remove_image(image_id)
        remove_all_volumes()
        remove_container(container_id)

    def test_creating_a_container_with_readonly_volume(self):
        volume_name = "cont_ro_vol1"
        image_name = "img_volro:latest"

        create_volume(volume_name)
        create_dockerfile(self.instructions)
        image_id = create_image(tag=image_name)
        container_id = create_container(
            name="test_cont_ro_vol",
            volumes=[f"{volume_name}:/testdir1:ro", "/testdir2:ro"],
            image=image_name,
            command="/usr/bin/touch /testdir1/testfile",
        )
        expected_output = [
            'touch: ', '/testdir1/testfile', ': ',
            'Read-only file system', '', 'jail: ',
            '/usr/bin/env -i /usr/bin/touch /testdir1/testfile: failed'
        ]
        *output, _,_,_,_ = run(f"container start --attach {container_id}")
        assert output == expected_output
        assert len(list_volumes()) == 2
        remove_image(image_id)
        remove_all_volumes()
        remove_container(container_id)


def create_volume(name):
    output = run(f"volume create {name}")
    return output


def empty_volume_list():
    expected_output = ['VOLUME NAME    CREATED', '-------------  ---------', '', '']
    output = run("volume ls")
    return expected_output == output


def remove_volume(volume_name):
    network_id, _ = run(f"volume rm {volume_name}")
    return network_id


def list_volumes():
    output = run("volume ls")
    _header,_headerline, *volumes, _, _ = output
    return [volume.split(" ")[0] for volume in volumes]


def remove_all_volumes():
    volumes = list_volumes()
    if len(volumes) > 0:
        volumes = " ".join(volumes)
        output = run(f"volume rm {volumes}")
