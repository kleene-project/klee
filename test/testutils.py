import json
import os

from click.testing import CliRunner
from rich.console import Console

from klee.main import cli
from klee.image import BUILD_START_MESSAGE


def container_stopped_msg(exec_id, exit_code=0):
    return f"executable {exec_id} and its container exited with exit-code {exit_code}"


def extract_exec_id(container_output):
    return container_output[0].split(" ")[-1]


def create_dockerfile(instructions, name="Dockerfile"):
    dockerfile = os.path.join(os.getcwd(), name)
    with open(dockerfile, "w", encoding="utf8") as f:
        f.write("\n".join(instructions))


def build_image(
    tag=None,
    dockerfile="Dockerfile",
    path=None,
    cleanup=True,
    quiet=True,
    buildargs=None,
):
    if path is None:
        path = os.getcwd()

    if buildargs is None:
        buildargs = ""
    else:
        buildargs = " ".join(
            [f"--build-arg {arg}={value}" for arg, value in buildargs.items()]
        )
        buildargs += " "

    dockerfile = f"--file {dockerfile} "
    tag = "" if tag is None else f"--tag {tag} "
    quiet = "--quiet " if quiet else ""
    cleanup = "--cleanup " if cleanup else "--no-cleanup "

    result = run(f"image build {buildargs}{tag}{quiet}{cleanup}{dockerfile}{path}")
    return result


def decode_invalid_image_build(result):
    error_msg_prefix = "Failed to build image"
    assert result[-2][: len(error_msg_prefix)] == error_msg_prefix
    image_id = _extract_id(result)
    build_log = result[1:-3]
    return image_id, build_log


def decode_valid_image_build(result):
    assert result[-3] == "image created"
    image_id = _extract_id(result)
    build_log = result[1:-3]
    return image_id, build_log


def create_image(method, tag=None, url=None, dataset=None):
    tag = "" if tag is None else f"--tag={tag} "
    dataset = "" if dataset is None else f"{dataset}"
    url = "" if url is None else f"--url={url}"

    result = run(f"image create {method} {tag}{url}{dataset}")
    return result


def remove_image(image_id):
    return run(f"image rm {image_id}")


def _extract_id(result):
    result_line = result[0]
    prefix = rich_render(BUILD_START_MESSAGE.format(image_id=""))

    id_ = None
    n = len(prefix)
    if result_line[:n] == prefix:
        id_ = result_line[n:]
    return id_


def remove_all_containers():
    _header, _lines, *containers = run("container ls -a")
    container_ids = []
    for line in containers[:-1]:
        lines = line.split(" ")
        container_id = lines[1]
        if container_id == "":
            continue
        container_ids.append(container_id)

    if len(container_ids) != 0:
        run("container rm " + " ".join(container_ids))


def remove_all_images():
    _header, _lines, *images = run("image ls")
    image_ids = []
    for line in images:
        image_id, *_rest = line.split(" ")
        if image_id == "":
            continue
        if image_id == "base":
            continue
        image_ids.append(image_id)

    if len(image_ids) != 0:
        run("image rm " + " ".join(image_ids))


def create_container(
    image="base", name=None, command="/bin/ls", volumes=None, network=None, ip=None
):

    if volumes is None:
        volumes = ""
    else:
        volumes = "".join([f"--volume {vol} " for vol in volumes])
    if network is None:
        network = ""
    else:
        network = f"--network {network} "

    if name is None:
        name = ""
    else:
        name = f"--name {name} "

    if ip is None:
        ip = ""
    else:
        ip = f"--ip {ip} "

    container_id, _ = run(
        f"container create {volumes}{network}{ip}{name}{image} {command}"
    )
    return container_id


def rich_render(message):
    console = Console()
    with console.capture() as capture:
        console.print(message, end="")

    return capture.get()


def container_get_netstat_info(container_id, driver):
    output = run(f"container start --attach {container_id}")
    if driver == "vnet":
        _, _, netstat_info, *_ = output

    elif driver == "loopback":
        _, netstat_info, *_ = output

    netstat_info = json.loads(netstat_info)
    interface_info = netstat_info["statistics"]["interface"]
    return interface_info


def remove_container(name_or_id):
    container_id, _ = run(f"container rm {name_or_id}")
    assert len(container_id) == 12
    return container_id


def run(command, exit_code=0):
    runner = CliRunner()
    result = runner.invoke(cli, command.split(" "))
    print(f'ran "{command}":{result.exit_code}: {result.output}')
    assert result.exit_code == exit_code
    return result.output.split("\n")
