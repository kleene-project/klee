from testutils import (
    create_dockerfile,
    create_image,
    decode_valid_image_build,
    remove_all_containers,
    remove_all_images,
    remove_image,
    run,
)


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
        result = create_image()
        _build_id, image_id, _build_log = decode_valid_image_build(result)
        images = list_images()
        image_id_listed = images[0][:12]
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)
        assert empty_image_list()

    def test_build_image_receive_build_messages(self):
        create_dockerfile(self.instructions)
        result = create_image(quiet=False)
        _build_id, image_id, build_log = decode_valid_image_build(result)
        expected_build_output = [
            "Step 1/3 : FROM scratch",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "Step 3/3 : CMD /usr/bin/uname",
        ]
        assert build_log == expected_build_output
        images = list_images()
        image_id_listed = images[0][:12]
        assert image_id == image_id_listed
        assert succesfully_remove_image(image_id)
        assert empty_image_list()

    def test_build_and_remove_and_with_a_tag(self):
        create_dockerfile(self.instructions)
        result = create_image(tag="testlol:testest")
        _build_id, image_id, _build_log = decode_valid_image_build(result)
        images = list_images()
        image_id_listed = images[0][:12]
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
        result = create_image(quiet=False)
        build_id, _image_id, build_log = decode_valid_image_build(result)
        expected_build_output = [
            "Step 1/3 : FROM scratch",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "Step 3/3 : RUN ls notexist",
            "ls: notexist: No such file or directory",
            "jail: /usr/bin/env -i /bin/sh -c ls notexist: failed",
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


def empty_image_list():
    HEADER = "ID    NAME    TAG    CREATED"
    LINE = "----  ------  -----  ---------"
    output = tuple(run("image ls"))
    return output == (HEADER, LINE, "", "")
