from testutils import (
    create_dockerfile,
    build_image,
    decode_valid_image_build,
    decode_invalid_image_build,
    create_image,
    remove_all_containers,
    remove_all_images,
    remove_image,
    run,
)


class TestImageCreateSubcommand:
    def test_create_image_with_fetch_method(self):
        url = "file:///home/vagrant/kleened/test/data/base_rescue.txz"
        result = create_image("fetch", tag="ImageCreate:test-fetch", url=url)
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)

    def test_create_image_with_zfs_method(self):
        dataset = "zroot/kleene_testdataset"
        result = create_image("zfs", tag="ImageCreate:test-zfs", dataset=dataset)
        assert result[-3] == "image created"
        image_id = result[-2]
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)


class TestImageSubcommand:
    # pylint: disable=no-self-use
    instructions = [
        "FROM scratch",
        'RUN echo "lol" > /root/test.txt',
        "CMD /usr/bin/uname",
    ]

    @classmethod
    def setup_class(cls):
        remove_all_containers()
        remove_all_images()

    def test_empty_listing_of_images(self):
        remove_all_images()
        assert empty_image_list()

    def test_build_remove_and_list_images(self):
        create_dockerfile(self.instructions)
        result = build_image()
        _build_id, image_id, _build_log = decode_valid_image_build(result)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)
        assert empty_image_list()

    def test_build_image_receive_build_messages(self):
        create_dockerfile(self.instructions)
        result = build_image(quiet=False)
        _build_id, image_id, build_log = decode_valid_image_build(result)
        expected_build_output = [
            "Step 1/3 : FROM scratch",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "Step 3/3 : CMD /usr/bin/uname",
            "",
        ]
        assert build_log == expected_build_output
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)
        assert empty_image_list()

    def test_build_and_remove_and_with_a_tag(self):
        create_dockerfile(self.instructions)
        result = build_image(tag="testlol:testest")
        _build_id, image_id, _build_log = decode_valid_image_build(result)
        image_id_listed = image_id_from_list(0)
        assert image_id == image_id_listed
        expected_image_entry = f"{image_id}  testlol  testest  Less than a second"
        assert list_images()[0] == expected_image_entry
        assert succesfully_remove_image(image_id)
        assert empty_image_list()

    def test_failed_build_without_cleanup(self):
        instructions = [
            "FROM scratch",
            'RUN echo "lol" > /root/test.txt',
            "RUN ls notexist",
        ]
        create_dockerfile(instructions)
        result = build_image(quiet=False)
        build_id, build_log = decode_invalid_image_build(result)
        expected_build_output = [
            "Step 1/3 : FROM scratch",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "Step 3/3 : RUN ls notexist",
            "ls: notexist: No such file or directory",
            "jail: /usr/bin/env -i /bin/sh -c ls notexist: failed",
            "executing instruction resulted in non-zero exit code",
        ]
        assert build_log == expected_build_output
        output = run(f"exec -a build_{build_id} /bin/cat /root/test.txt", exit_code=0)

        prefix = "created execution instance "
        assert output[0][: len(prefix)] == prefix
        assert output[1] == "lol"
        assert empty_image_list()


def succesfully_remove_image(image_id):
    output = remove_image(image_id)
    return output[0] == image_id


def list_images():
    _, _, *images = run("image ls")
    return images


def image_id_from_list(index):
    images = list_images()
    image_id = images[index][:12]
    return image_id


def empty_image_list():
    HEADER = "ID    NAME    TAG    CREATED"
    LINE = "----  ------  -----  ---------"
    output = tuple(run("image ls"))
    return output == (HEADER, LINE, "", "")
