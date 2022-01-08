import subprocess

from click.testing import CliRunner

from jcli.main import cli


class TestContainers:
    @classmethod
    def setup_class(cls):
        _header, _lines, *containers = run('container ls -a')
        container_ids = []
        for container_line in containers:
            container_id, *_rest = container_line.split(" ")
            if container_id == "":
                continue
            container_ids.append(container_id)

        if len(container_ids) != 0:
            run('container rm ' + ' '.join(container_ids))

    # pylint: disable=no-self-use
    def test_empty_container_listing_of_containers(self):
        assert empty_container_list(all_=False)
        assert empty_container_list(all_=True)

    def test_add_remove_and_list_containers(self):
        name = "test_adl_containers"
        container_id = create_container(name=name)
        assert len(container_id) == 12

        assert empty_container_list(all_=False)
        _header, _lines, container, *_ = run('container ls -a')
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
        container_id_again, _ = run(f"container start {container_id}")
        assert container_id == container_id_again
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
        container_id_again, _ = run(f"container start {container_id[:8]}")
        assert container_id == container_id_again
        assert container_is_running(container_id)
        container_id_again, _ = run(f"container stop {container_id[:8]}")
        assert container_id == container_id_again
        remove_container(container_id)


    def test_start_attached_container(self):
        name = "test_attached_container"
        container_id = create_container(name=name, command="/usr/bin/uname")
        container_output = run(f"container start --attach {container_id}")
        exit_msg = f"exit:container {container_id} stopped"
        assert container_output == ['FreeBSD', '', exit_msg, '']
        remove_container(container_id)



HEADER = "CONTAINER ID    IMAGE    TAG    COMMAND    CREATED    STATUS    NAME"
LINE = "--------------  -------  -----  ---------  ---------  --------  ------"


def run(command, exit_code=0):
    runner = CliRunner()
    command = command.split(" ")
    result = runner.invoke(cli, command)
    print(f"ran '{command}':{result.exit_code}: {result.output}")
    assert result.exit_code == exit_code
    return result.output.split('\n')


def create_container(image="base", name=None, command="/bin/ls"):
    if name is None:
        name = ""
    else:
        name = f"--name {name} "
    container_id, _ = run(f"container create {name}{image} {command}")
    return container_id


def remove_container(name_or_id):
    container_id, _ = run(f"container rm {name_or_id}")
    return container_id


def container_is_running(container_id):
    # If grep have at least one match it returns statuscode 0, otherwise 1
    result = subprocess.run(["/bin/sh", "-c", f"jls | grep {container_id}"], check=False)
    return result.returncode == 0


def empty_container_list(all_=True):
    if all_:
        output = tuple(run('container ls -a'))
    else:
        output = tuple(run('container ls'))
    return output == (HEADER, LINE, "", "")


def container_list(all_=True):
    """Returns a tuple of container_ids from the 'container ls' command"""
    if all_:
        output = run('container ls -a')
    else:
        output = run('container ls')
    output = output[2:-2] # exclude header + postfixed line-endings
    container_ids = [row[:12] for row in output]
    return tuple(container_ids)
