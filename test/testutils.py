import subprocess
import json
import os

import httpx
from click.testing import CliRunner
from rich.console import Console

from klee.client.api.default.image_list import sync_detailed as image_list_endpoint
from klee.client.api.default.container_list import (
    sync_detailed as container_list_endpoint,
)
from klee.client.client import Client
from klee.root import create_cli
from klee.image import BUILD_START_MESSAGE

SELF_SIGNED_ERROR = "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain"

CERTIFICATE_REQUIRED_ERROR = "unable to connect to kleened: [SSL: TLSV13_ALERT_CERTIFICATE_REQUIRED] tlsv13 alert certificate required"

EMPTY_CONTAINER_LIST = [
    " CONTAINER ID    NAME   IMAGE   COMMAND   CREATED   AUTORUN   STATUS   JID ",
    "───────────────────────────────────────────────────────────────────────────",
    "",
]


def jail_info():
    result = subprocess.run(
        args=["/usr/sbin/jls", "--libxo", "json"], check=True, capture_output=True
    )
    return json.loads(result.stdout)


def shell(command):
    return shell_raw(command).stdout.decode("utf8")


def shell_raw(cmd):
    print_running_command(cmd, "shell")
    result = subprocess.run(cmd, shell=True, check=False, capture_output=True)
    print_command_exit(result.returncode, result.stdout, "shell")
    return result


def container_stopped_msg(exec_id, exit_code=0):
    return f"executable {exec_id} and its container exited with exit-code {exit_code}"


def extract_exec_id(container_output):
    return container_output[0].split(" ")[-1]


def create_dockerfile(instructions, name="Dockerfile"):
    dockerfile = os.path.join(os.getcwd(), name)
    with open(dockerfile, "w", encoding="utf8") as f:
        f.write("\n".join(instructions) + "\n")


def stat(file_name):
    """
    Example:

    $ stat -f "%Dm %Sm %Sp" ~/Makefile
    1712050233 apr.  2 09:30:33 2024 -rw-r--r--
    """
    return f"stat -f %Dm,%Sm,%Sp {file_name}"


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
    cleanup = "--rm " if cleanup else ""
    shell("zfs list")
    shell("pwd")
    shell("ls -a")
    run("lsi")
    run("lsc -a")
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


def remove_all_images():
    _header, _lines, *images = run("image ls")
    image_ids = []
    for line in images[:-1]:
        image_id, name, tag, *_rest = line.split(" ")
        if image_id == "":
            continue
        if name == "FreeBSD" and tag == "latest":
            continue
        image_ids.append(image_id)

    if len(image_ids) != 0:
        run("image rm " + " ".join(image_ids))


def create_container(
    image="FreeBSD:latest",
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


def prune(obj_type, all_=False):
    if all_:
        output = run(f"{obj_type} prune --all -f")
    else:
        output = run(f"{obj_type} prune -f")

    return output[:-1]


def inspect(obj_type, identifier):
    output = run(f"{obj_type} inspect {identifier}")
    output = "".join(output)
    try:
        return json.loads(output)
    except json.decoder.JSONDecodeError:
        return output


def list_images():
    kwargs = {}
    response = image_list_endpoint(
        httpx.HTTPTransport(uds="/var/run/kleened.sock"),
        client=Client(base_url="http://localhost"),
        **kwargs,
    )
    return response.parsed


def list_containers(all_=True):
    kwargs = {"all_": all_}
    response = container_list_endpoint(
        httpx.HTTPTransport(uds="/var/run/kleened.sock"),
        client=Client(base_url="http://localhost"),
        **kwargs,
    )
    return response.parsed


def container_netstat(container_id):
    return run(f"container exec {container_id} /usr/bin/netstat --libxo json -i -4")


def container_get_netstat_info(container_id, driver):
    output = run(f"container exec {container_id}")
    if driver == "vnet":
        netstat_info = "".join(output[2:-3])

    elif driver == "loopback":
        netstat_info = "".join(output[1:-3])

    netstat_info = json.loads(netstat_info)
    interface_info = netstat_info["statistics"]["interface"]
    return interface_info


def run(command, exit_code=0):
    if isinstance(command, str):
        command = command.split(" ")

    _clear_config()
    runner = CliRunner()
    cli = create_cli()
    print_running_command(" ".join(command), "klee")
    result = runner.invoke(cli, command, catch_exceptions=False)
    print_command_exit(result.exit_code, result.output, "klee")

    assert result.exit_code == exit_code
    if command[0] == "rmc" or command[:2] == ["container", "rm"]:
        container_id = result.output[:-1]
        return container_id

    if command[0] == "run" or command[:2] == ["container", "run"]:
        if result.exit_code == 0:
            if "-d" in command or "--detach" in command:
                container_id, exec_msg, _nl = result.output.split("\n")
                exec_id = exec_msg.split(" ")[-1]
                return container_id, exec_id, []

            container_id, exec_msg, *output, _endmsg, _nl = result.output.split("\n")
            exec_id = exec_msg.split(" ")[-1]
            return container_id, exec_id, output

    return result.output.split("\n")


def print_running_command(command, type_):
    print(f">>>running {type_} command: {command}")


def print_command_exit(exit_code, output, type_):
    print(f">>>{type_} command exited with code {exit_code}:\n{output}")


def _clear_config():
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


def _extract_id(result):
    result_line = result[0]
    prefix = rich_render(BUILD_START_MESSAGE.format(image_id=""))

    id_ = None
    n = len(prefix)
    if result_line[:n] == prefix:
        id_ = result_line[n:]
    return id_
