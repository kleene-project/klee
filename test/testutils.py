import subprocess
import json
import os
import re

import httpx
from click.testing import CliRunner
from rich.console import Console

from klee.client.api.default.image_list import sync_detailed as image_list_endpoint
from klee.client.api.default.container_list import (
    sync_detailed as container_list_endpoint,
)
from klee.client.api.default.volume_list import sync_detailed as volume_list_endpoint
from klee.client.api.default.network_list import sync_detailed as network_list_endpoint
from klee.client.client import Client
from klee.root import create_cli
from klee.image import BUILD_START_MESSAGE
from klee.deploy import DEFAULT_DEPLOYMENT_FILE

SELF_SIGNED_ERROR = "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain"

CERTIFICATE_REQUIRED_ERROR = "unable to connect to kleened: [SSL: TLSV13_ALERT_CERTIFICATE_REQUIRED] tlsv13 alert certificate required"

KLEENE_ROOT = "zroot/kleene"
BASEJAIL = "zroot/kleene_basejail"
TEST_IMAGE = "FreeBSD:latest"


def create_deployment_file(content, path=DEFAULT_DEPLOYMENT_FILE):
    with open(path, "w", encoding="utf8") as deploy_file:
        deploy_file.write(content)


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


def create_dockerfile(instructions, path=None, parent=None, name="Dockerfile"):
    if parent is not None:
        instructions.insert(0, f"FROM {parent}")

    if path is None:
        path = os.getcwd()
    else:
        os.makedirs(path, exist_ok=True)

    dockerfile = os.path.join(path, name)
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
    return run(f"image build {buildargs}{tag}{quiet}{cleanup}{dockerfile}{path}")


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


def list_volumes():
    kwargs = {}
    response = volume_list_endpoint(
        httpx.HTTPTransport(uds="/var/run/kleened.sock"),
        client=Client(base_url="http://localhost"),
        **kwargs,
    )
    return response.parsed


def list_networks():
    kwargs = {}
    response = network_list_endpoint(
        httpx.HTTPTransport(uds="/var/run/kleened.sock"),
        client=Client(base_url="http://localhost"),
        **kwargs,
    )
    return response.parsed


def container_ip(container_id):
    """The container's first IPv4 endpoint address, via 'container inspect'."""
    inspected = inspect("container", container_id)
    endpoints = inspected["container_endpoints"]
    for endpoint in endpoints:
        if endpoint.get("ip_address"):
            return endpoint["ip_address"]
    return None


def container_interfaces(container_id, ipv4_only=False):
    """
    The 'statistics.interface' list that netstat(1) reports inside a container.

    The container does not have to be running: the exec'd command replaces the
    container's own command, and a stopped container is started to run it.

    'ipv4_only' restricts the listing to interfaces with an IPv4 address.

    klee interleaves its own status lines with the container's output, so the
    JSON document is found by skipping the lines klee is known to emit.
    """
    netstat = "netstat --libxo json -n -i"
    if ipv4_only:
        netstat = f"{netstat} -4"

    output = run(["exec", container_id, "/bin/sh", "-c", netstat])
    interfaces = json.loads(_first_non_klee_message(output))
    return interfaces["statistics"]["interface"]


def listing_rows(output):
    """One entry per object listed by 'klee <object> ls'."""
    header, _rule, *lines = output
    width = _first_column_width(header)

    rows = []
    for line in lines[:-1]:
        if line[:width].strip():
            rows.append(line)
        elif rows:
            rows[-1] = f"{rows[-1]} {line.strip()}"

    return rows


def listing_ids(output):
    """First column of every row of a listing -- the ID, or the name for volumes."""
    return [row.split()[0] for row in listing_rows(output)]


def _first_column_width(header):
    """
    Where the first column of a listing ends.

    Column labels may contain single spaces ('CONTAINER ID'), so the boundary is
    the first run of two or more spaces.
    """
    match = re.search(r"\S\s{2,}", header)
    return match.end() if match is not None else len(header)


def assert_empty_listing(command):
    """Assert that a 'klee <object> ls' command lists nothing."""
    output = run(command)
    rows = listing_rows(output)
    assert rows == [], "expected an empty listing, got:\n" + "\n".join(output)


def run(command, exit_code=0):
    """
    Invoke klee and return its output, one list element per line.

    'run_container' and 'remove_container' exist for the two commands whose
    output is worth decoding further -- this returns lines for every command,
    including those two.
    """
    result = _invoke(command, exit_code)
    return result.output.split("\n")


def run_container(command, exit_code=0):
    """
    Invoke 'klee run' (or 'klee container run') and decode its output.

    Returns '(container_id, exec_id, output_lines)'. For a detached run there is
    no container output, so the third element is an empty list.
    """
    if isinstance(command, str):
        command = command.split(" ")

    assert command[0] == "run" or command[:2] == ["container", "run"]
    result = _invoke(command, exit_code)

    if "-d" in command or "--detach" in command:
        container_id, exec_msg, _nl = result.output.split("\n")
        return container_id, exec_msg.split(" ")[-1], []

    container_id, exec_msg, *output, _endmsg, _nl = result.output.split("\n")
    return container_id, exec_msg.split(" ")[-1], output


def remove_container(command, exit_code=0):
    """Invoke 'klee rmc' (or 'klee container rm') and return the removed container id."""
    result = _invoke(command, exit_code)
    return result.output[:-1]


def _invoke(command, exit_code):
    if isinstance(command, str):
        command = command.split(" ")

    _clear_config()
    runner = CliRunner()
    cli = create_cli()
    print_running_command(" ".join(command), "klee")
    result = runner.invoke(cli, command, catch_exceptions=False)
    print_command_exit(result.exit_code, result.output, "klee")

    assert result.exit_code == exit_code, (
        f"'klee {' '.join(command)}' exited with {result.exit_code}, "
        f"expected {exit_code}. Output was:\n{result.output}"
    )
    return result


def _first_non_klee_message(output):
    """The first line of output that klee itself did not emit."""

    def remove_standard_messages(line):
        if line.startswith("created execution instance"):
            return False

        if line.startswith("add net default: gateway"):
            return False

        return True

    return next(filter(remove_standard_messages, output))


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


def get_host_state():
    """The host state a clean run must return to: datasets, basejail
    snapshots, interfaces, and devfs/nullfs mounts under the kleene root."""
    return {
        "zfs": _shell_lines("zfs list -H -o name -r zroot/kleene"),
        "snapshots": _shell_lines(
            "zfs list -t snapshot -H -o name,clones -d 1 zroot/kleene_basejail"
        ),
        "interfaces": set(shell("ifconfig -l").split()),
        "mounts": [
            line
            for line in shell("mount").split("\n")
            if ("devfs" in line or "nullfs" in line) and "zroot/kleene" in line
        ],
    }


def assert_clean_host_state(baseline):
    """Assert the host is back to the captured baseline. Run after
    sweep_host_state(), so what this catches is residue the sweep cannot
    remove: a leaked jail, an interface never destroyed, a mount left
    behind."""
    now = get_host_state()
    assert baseline["zfs"] == now["zfs"], (
        f"dataset diff: {baseline['zfs'] ^ now['zfs']}"
    )
    assert baseline["snapshots"] == now["snapshots"], (
        f"basejail snapshot diff: {baseline['snapshots'] ^ now['snapshots']}"
    )
    assert baseline["interfaces"] == now["interfaces"], (
        f"interface diff: {baseline['interfaces'] ^ now['interfaces']}"
    )
    assert baseline["mounts"] == now["mounts"], f"mount diff: {now['mounts']}"


def sweep_host_state():
    """Convergent sweep of all kleene-owned host state except the
    FreeBSD:latest test image. Idempotent: a second call is a no-op.

    Removal order matters: containers first (jails hold mounts and
    interfaces), then orphan datasets (they pin image datasets as clone
    origins), then metadata-driven removal of volumes / networks /
    images, then host-side sweeps for what metadata no longer knows.
    """
    _sweep_containers()
    _sweep_orphan_datasets()
    _sweep_volumes()
    _sweep_networks()
    _sweep_interfaces()
    _sweep_mounts()
    _sweep_basejail_snapshots()
    _sweep_images()


def _shell_lines(command):
    return set(shell(command).strip().split("\n")) - {""}


def _sweep_containers():
    for container in list_containers():
        run(f"container rm -f {container.id}")
    # jail teardown lags the API response; poll actual liveness
    for _ in range(50):
        if shell("jls -n name").strip() == "":
            return
        shell("sleep 0.1")


def _known_datasets():
    known = []
    for container in list_containers():
        known.append(container.dataset)
    for image in list_images():
        known.append(image.dataset)
    for volume in list_volumes():
        known.append(volume.dataset)
    return set(known)


def _sweep_orphan_datasets():
    known = _known_datasets()
    for sub in ("container", "image", "volumes"):
        root = f"{KLEENE_ROOT}/{sub}"
        actual = _shell_lines(f"zfs list -H -o name -r {root}")
        for orphan in actual - known - {root}:
            shell(f"zfs destroy -f -r {orphan}")


def _sweep_volumes():
    for volume in list_volumes():
        run(f"volume rm {volume.name}")


def _sweep_networks():
    for network in list_networks():
        run(f"network rm {network.id}")


def _sweep_interfaces():
    # kleene interfaces are all named 'kleene<id>'; with networks removed,
    # any survivor is residue from a crashed network removal.
    for interface in shell("ifconfig -l").split():
        if interface.startswith("kleene"):
            shell(f"ifconfig {interface} destroy")


def _sweep_mounts():
    # devfs/nullfs mounts under the kleene root are left behind when a
    # jail dies without 'jail -r' teardown.
    for line in shell("mount").split("\n"):
        if ("devfs" in line or "nullfs" in line) and "zroot/kleene" in line:
            mountpoint = line.split(" on ")[1].split(" (")[0]
            shell(f"umount -f {mountpoint}")


def _sweep_basejail_snapshots():
    # snapshots on the basejail with no live clone are garbage; the only
    # legitimate clone is a known image dataset, e.g. FreeBSD:latest's
    # origin. '-d' keeps the destroy safe should a clone appear between
    # listing and destroying.
    output = shell("zfs list -t snapshot -H -o name,clones -d 1 zroot/kleene_basejail")
    snapshots = []
    for line in output.strip().split("\n"):
        if not line:
            continue
        name, clones = line.split("\t")
        if clones == "-":
            snapshots.append(name.split("@")[-1])
    for i in range(0, len(snapshots), 500):
        chunk = ",".join(snapshots[i : i + 500])
        shell(f"zfs destroy -d {BASEJAIL}@{chunk}")


def _sweep_images():
    # everything except the class-scoped test image, whose lifecycle
    # create_testimage owns
    for image in list_images():
        if f"{image.name}:{image.tag}" != TEST_IMAGE:
            run(f"image rm {image.id}")
