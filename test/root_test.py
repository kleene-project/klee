import subprocess
import os

import yaml

from testutils import run, CERTIFICATE_REQUIRED_ERROR

from klee.config import create_default_config_locations
from klee.root import DEFAULT_HOST, ERROR_INVALID_CONFIG
from klee.connection import ERROR_TLSKEY_WITH_TLSCERT

config_filepaths = create_default_config_locations()

HTYP_ERROR = (
    "unable to connect to kleened: Request URL has an unsupported protocol 'htyp://'."
)

EMPTY_CONTAINER_LIST = [
    " CONTAINER ID    NAME   IMAGE   TAG   COMMAND   CREATED   STATUS ",
    "─────────────────────────────────────────────────────────────────",
]

CUSTOM_CONFIG = "./test_config.yaml"

# With this 'translation' both linux and *bsd platforms should work
level2filepaths = {
    "cwd": config_filepaths[0],
    "homedir": config_filepaths[1],
    "systemdir": config_filepaths[2],
    "custom": CUSTOM_CONFIG,
}


def remove_all_configs():
    for filepath in config_filepaths:
        try:
            os.remove(os.path.expanduser(filepath))
        except FileNotFoundError:
            print("Did not exist")
            continue


def default_connection_configured():
    output = run("container ls")
    assert output[:-1] == EMPTY_CONTAINER_LIST


def htyp_configured():
    output = run("container ls")
    assert output[:-1] == [HTYP_ERROR]


class TestFileConfiguration:
    def setup_method(self):
        remove_all_configs()

    def teardown_method(self):
        remove_all_configs()

    def test_filepaths(self):
        config = {"host": "htyp:///var/sock"}
        for level in ["cwd", "homedir", "systemdir"]:
            _create_config_file(config, level)
            htyp_configured()
            remove_all_configs()
            default_connection_configured()

    def test_multiple_config_file_priority(self):
        config_high_priority = {"host": "https://127.0.0.1:8085", "tlsverify": False}
        config_low_priority = {"host": DEFAULT_HOST}
        _create_config_file(config_high_priority, "cwd")
        _create_config_file(config_low_priority, "homedir")
        output = run("container ls")
        assert "".join(output) == CERTIFICATE_REQUIRED_ERROR

    def test_envvar_takes_priority(self):
        config_file = {"host": DEFAULT_HOST}
        _create_config_file(config_file, "cwd")
        # Testing in a completely fresh environment so we don't mess with envvars etc.
        output = subprocess.run(
            'KLEE_HOST="https://127.0.0.1:8085" KLEE_TLS_VERIFY=false klee container ls',
            shell=True,
            capture_output=True,
            check=False,
        )
        output = output.stdout.decode("utf8").replace("\n", "")
        assert output == CERTIFICATE_REQUIRED_ERROR

    def test_command_line_config_takes_priority(self):
        config_high_priority = {"host": "https://127.0.0.1:8085", "tlsverify": False}
        config_low_priority = {"host": DEFAULT_HOST}
        _create_config_file(config_high_priority, "custom")
        _create_config_file(config_low_priority, "cwd")
        # Testing in a completely fresh environment so we don't mess with envvars etc.
        output = subprocess.run(
            f'KLEE_CONFIG="$(pwd)/klee_config.yaml" klee --config {CUSTOM_CONFIG} container ls',
            shell=True,
            capture_output=True,
            check=False,
        )
        output = output.stdout.decode("utf8").replace("\n", "")
        assert output == CERTIFICATE_REQUIRED_ERROR

    def test_invalid_no_tlskey(self):
        config = {
            "host": "https://127.0.0.1:8085",
            "tlscert": "/usr/local/etc/kleened/certs/client-cert.pem",
        }
        _create_config_file(config, "systemdir")
        output = run("container ls")
        assert "".join(output) == ERROR_TLSKEY_WITH_TLSCERT

    def test_invalid_config(self):
        config = {"host": DEFAULT_HOST, "nonexistingparameter": "test"}
        _create_config_file(config, "cwd")
        output = run("container ls", exit_code=-1)

        assert "".join(output) == ERROR_INVALID_CONFIG.format(
            filepath=level2filepaths["cwd"], parameter="nonexistingparameter"
        )


def _create_config_file(content, level):
    # In case of the '~/' directory
    filepath = os.path.expanduser(level2filepaths[level])
    with open(filepath, "w", encoding="utf8") as f:
        f.write(yaml.dump(content))
