import subprocess

from testutils import (
    create_container,
    remove_all_containers,
    remove_container,
    extract_exec_id,
    run,
)


class TestContainerSubcommand:
    @classmethod
    def setup_class(cls):
        remove_all_containers()

    # pylint: disable=no-self-use
    def test_empty_container_listing_of_containers(self):
        assert empty_container_list(all_=False)
        assert empty_container_list(all_=True)

    def test_add_remove_and_list_containers(self):
        name = "test_adl_containers"
        container_id = create_container(name=name)
        assert len(container_id) == 12

        assert empty_container_list(all_=False)
        _header, _lines, container, *_ = run("container ls -a")
        assert container[:12] == container_id

        container_id2, _ = run(f"container rm {name}")
        assert container_id2 == container_id

        assert empty_container_list()

    def test_remove_container_by_id(self):
        name = "test_remove"
        container_id1 = create_container()
        container_id2 = create_container(name=name)
        container_id1_again = remove_container(container_id1)
        container_id2_again = remove_container(container_id2)
        assert container_id1 == container_id1_again
        assert container_id2 == container_id2_again

    def test_starting_and_stopping_a_container_and_list_containers(self):
        container_id = create_container(name="test_start_stop", command="/bin/sleep 10")
        succes_msg, _newline = run(f"container start {container_id}")
        assert "created execution instance " == succes_msg[:27]
        assert container_is_running(container_id)
        assert (container_id,) == container_list(all_=False)
        container_id_again, _ = run(f"container stop {container_id}")
        assert container_id == container_id_again
        assert not container_is_running(container_id)
        assert not container_list(all_=False)
        container_id_again = remove_container(container_id)
        assert container_id == container_id_again

    def test_container_referencing(self):
        name = "test_container_referencing"
        container_id = create_container(name=name, command="/bin/sleep 10")
        succes_msg, _newline = run(f"container start {container_id[:8]}")
        assert "created execution instance " == succes_msg[:27]
        assert container_is_running(container_id)
        container_id_again, _ = run(f"container stop {container_id[:8]}")
        assert container_id == container_id_again
        remove_container(container_id)

    def test_start_attached_container(self):
        name = "test_attached_container"
        container_id = create_container(name=name, command="/usr/bin/uname")
        container_output = run(f"container start --attach {container_id}")
        exec_id = extract_exec_id(container_output)
        expected_output = [
            f"created execution instance {exec_id}",
            "FreeBSD",
            "",
            f"executable {exec_id} stopped",
        ]
        assert container_output == expected_output
        remove_container(container_id)


def container_is_running(container_id):
    # If grep have at least one match it returns statuscode 0, otherwise 1
    result = subprocess.run(
        ["/bin/sh", "-c", f"jls | grep {container_id}"], check=False
    )
    return result.returncode == 0


def empty_container_list(all_=True):
    HEADER = "CONTAINER ID    IMAGE    TAG    COMMAND    CREATED    STATUS    NAME"
    LINE = "--------------  -------  -----  ---------  ---------  --------  ------"

    if all_:
        output = tuple(run("container ls -a"))
    else:
        output = tuple(run("container ls"))
    return output == (HEADER, LINE, "", "")


def container_list(all_=True):
    """Returns a tuple of container_ids from the 'container ls' command"""
    if all_:
        output = run("container ls -a")
    else:
        output = run("container ls")
    output = output[2:-2]  # exclude header + postfixed line-endings
    container_ids = [row[:12] for row in output]
    return tuple(container_ids)
