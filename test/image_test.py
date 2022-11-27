from testutils import (
    create_dockerfile,
    create_image,
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
        _, image_id_created = result[0].split(" id ")
        images = list_images()
        image_id_listed = images[0][:12]
        assert image_id_created == image_id_listed
        assert succesfully_remove_image(image_id_created)
        assert empty_image_list()

    def test_build_image_receive_build_messages(self):
        create_dockerfile(self.instructions)
        result = create_image(quiet=False)
        build_output = result[:-2]
        expected_build_output = [
            "Step 1/3 : FROM scratch",
            "",
            'Step 2/3 : RUN echo "lol" > /root/test.txt',
            "",
            "Step 3/3 : CMD /usr/bin/uname",
        ]
        assert build_output == expected_build_output
        _, image_id_created = result[-1].split(" id ")
        images = list_images()
        image_id_listed = images[0][:12]
        assert image_id_created == image_id_listed
        assert succesfully_remove_image(image_id_created)
        assert empty_image_list()

    def test_build_and_remove_and_with_a_tag(self):
        create_dockerfile(self.instructions)
        result = create_image(tag="testlol:testest")
        _, image_id_created = result[0].split(" id ")
        images = list_images()
        image_id_listed = images[0][:12]
        assert image_id_created == image_id_listed

        expected_image_entry = (
            f"{image_id_created}  testlol  testest  Less than a second"
        )
        assert list_images()[0] == expected_image_entry
        assert succesfully_remove_image(image_id_created)
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
