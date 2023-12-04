import subprocess
import json
import os

from click.testing import CliRunner
from rich.console import Console

from klee.root import create_cli
from klee.image import BUILD_START_MESSAGE

SELF_SIGNED_ERROR = "unable to connect to kleened: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1134)"

CERTIFICATE_REQUIRED_ERROR = "unable to connect to kleened: [SSL: TLSV13_ALERT_CERTIFICATE_REQUIRED] tlsv13 alert certificate required (_ssl.c:2638)"


def jail_info():
    result = subprocess.run(
        args=["/usr/sbin/jls", "--libxo", "json"], capture_output=True
    )
    return json.loads(result.stdout)


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


def create_image(method, tag=None, url=None, dataset=None, dns=True):
    tag = "" if tag is None else f"--tag={tag} "
    dns = "" if dns else "--no-dns "

    if method in {"zfs-copy", "zfs-clone"}:
        return run(f"image create {dns}{tag}{method} {dataset}")

    if method == "fetch":
        return run(f"image create {dns}{tag}{method} {url}")

    if method == "fetch-auto":
        return "fetch-auto method not supported"

    return f"unknown method type {method}"


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
    for line in images[:-1]:
        image_id, name, tag, *_rest = line.split(" ")
        if image_id == "":
            continue
        if name == "FreeBSD" and tag == "testing":
            continue
        image_ids.append(image_id)

    if len(image_ids) != 0:
        run("image rm " + " ".join(image_ids))


def create_container(
    image="FreeBSD:testing",
    name=None,
    command="/bin/ls",
    volumes=None,
    network=None,
    ip=None,
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


def prune(obj_type):
    output = run(f"{obj_type} prune -f")
    return output[:-1]


def inspect(obj_type, identifier):
    output = run(f"{obj_type} inspect {identifier}")
    output = "".join(output)
    try:
        return json.loads(output)
    except json.decoder.JSONDecodeError:
        return output


def container_get_netstat_info(container_id, driver):
    output = run(f"container start --attach {container_id}")
    if driver == "vnet":
        netstat_info = "".join(output[2:-3])

    elif driver == "loopback":
        netstat_info = "".join(output[1:-3])

    netstat_info = json.loads(netstat_info)
    interface_info = netstat_info["statistics"]["interface"]
    return interface_info


def remove_container(name_or_id):
    container_id, _ = run(f"container rm {name_or_id}")
    assert len(container_id) == 12
    return container_id


def run(command, exit_code=0):
    clear_config()
    runner = CliRunner()
    cli = create_cli()
    print(f'running command: "{command}"')
    result = runner.invoke(cli, command.split(" "), catch_exceptions=False)
    print(f"exited with code {result.exit_code}:\n{result.output}")
    assert result.exit_code == exit_code
    return result.output.split("\n")


def clear_config():
    from klee.config import config

    # To be sure, we clean the configuration parameters, because
    # during testing the config singleton object persists across several CLI invocations
    for param in config._config_params + [
        "invalid_file",
        "invalid_param",
        "config_filepath",
    ]:
        if param == "theme":
            continue

        setattr(config, param, None)
