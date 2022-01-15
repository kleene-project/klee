from click.testing import CliRunner

from jcli.main import cli


def run(command, exit_code=0):
    runner = CliRunner()
    command = command.split(" ")
    result = runner.invoke(cli, command)
    print(f"ran '{command}':{result.exit_code}: {result.output}")
    assert result.exit_code == exit_code
    return result.output.split('\n')


def remove_all_containers():
    _header, _lines, *containers = run('container ls -a')
    container_ids = []
    for line in containers:
        container_id, *_rest = line.split(" ")
        if container_id == "":
            continue
        container_ids.append(container_id)

    if len(container_ids) != 0:
        run('container rm ' + ' '.join(container_ids))


def remove_all_images():
    _header, _lines, *images = run('image ls')
    image_ids = []
    for line in images:
        image_id, *_rest = line.split(" ")
        if image_id == "":
            continue
        image_ids.append(image_id)

    if len(image_ids) != 0:
        run('image rm ' + ' '.join(image_ids))
