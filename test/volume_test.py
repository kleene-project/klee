from testutils import assert_empty_listing, inspect, listing_ids, prune, run


class TestVolumeSubcommand:
    instructions = [
        "FROM FreeBSD:testing",
        "RUN mkdir /testdir1",
        "RUN mkdir /testdir2",
    ]

    def test_add_remove_and_listing_volumes(self):
        name = "test_arl_volumes"
        assert_empty_listing("volume ls")
        assert name == create_volume(name)
        assert [name] == list_volumes()
        assert name == remove_volume(name)
        assert_empty_listing("volume ls")

    def test_listing_several_volumes(self):
        first = "test_list_volumes1"
        second = "test_list_volumes2"
        create_volume(first)
        create_volume(second)
        assert sorted(list_volumes()) == [first, second]

        remove_volume(second)
        assert list_volumes() == [first]
        remove_volume(first)

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

    def test_prune_volume_leaves_mounted_volumes_alone(self, testimage_and_cleanup):
        mounted = "test_volume_prune_mounted"
        unused = "test_volume_prune_unused"
        create_volume(name=mounted)
        create_volume(name=unused)
        # /mnt is empty in the basejail, so mounting over it hides nothing.
        run(f"container create --name volume_prune_test -m {mounted}:/mnt FreeBSD")

        assert prune("volume") == [unused]
        assert list_volumes() == [mounted]

        run("container prune -f")
        remove_volume(mounted)


def create_volume(name):
    output = run(f"volume create {name}")
    return output[0]


def remove_volume(volume_name):
    output = run(f"volume rm {volume_name}")
    return output[0]


def list_volumes():
    return listing_ids(run("volume ls"))


