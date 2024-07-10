import json
import yaml
import click

from .client.types import Unset
from .client.models.deployment_config import DeploymentConfig
from .client.api.default.deployment_diff import (
    sync_detailed as deployment_diff_endpoint,
)

from .printing import (
    echo_bold,
    group_cls,
    command_cls,
    print_response_msg,
    print_json_raw,
)
from .utils import request_and_print_response

# pylint: disable=unused-argument

DEFAULT_DEPLOYMENT_FILE = "deployment.yml"


@click.group(cls=group_cls())
def root(name="deploy"):
    """Manage deployment"""


def deploy_diff(name, hidden=False):

    @click.command(
        cls=command_cls(),
        name=name,
        hidden=hidden,
        short_help="Show the difference between a deployment spec and the host.",
    )
    @click.option(
        "--file",
        "-f",
        default="deployment.yml",
        show_default=True,
        help="Specify the deployment file to use.",
    )
    @click.option(
        "--json",
        default=False,
        is_flag=True,
        help="JSON-encode diff result",
    )
    def diff(**kwargs):
        """
        FIXME: Some useful help-description here.
        """
        with open(kwargs["file"], encoding="utf8") as deployment_file:
            deployment_yaml = deployment_file.read()

        deployment = yaml.safe_load(deployment_yaml)
        _add_container_defaults(deployment)
        _add_network_defaults(deployment)
        deployment = DeploymentConfig.from_dict(deployment).to_dict()

        # This mimics the behavoir of container.py:_create_container_and_connect_to_network
        for container in deployment["containers"]:
            if "network_driver" not in deployment and len(container["endpoints"]) == 0:
                container["network_driver"] = "host"

            if "network_driver" not in deployment and len(container["endpoints"]) > 0:
                container["network_driver"] = "ipnet"

        deployment_config = DeploymentConfig.from_dict(deployment)

        response = request_and_print_response(
            deployment_diff_endpoint,
            kwargs={"json_body": deployment_config},
            statuscode2printer={
                201: lambda x: None,
                409: print_response_msg,
                404: print_response_msg,
            },
        )

        result_json = response.content.decode("utf8")
        result_json = _adjust_result(result_json)

        if kwargs["json"]:
            print_json_raw(result_json)
        else:
            echo_bold("Implement me!")

    return diff


def _add_network_defaults(deployment):
    if "networks" in deployment:
        for network in deployment["networks"]:
            if "type" not in network:
                network["type"] = "loopback"


def _add_container_defaults(deployment):
    if "containers" in deployment:
        for container in deployment["containers"]:
            if "endpoints" in container:
                for endpoint in container["endpoints"]:
                    endpoint["container"] = container["name"]

                    if "ip_address" not in endpoint and "ip_address6" not in endpoint:
                        endpoint["ip_address"] = "<auto>"
                        endpoint["ip_address6"] = "<auto>"


def _adjust_result(result_json):
    result = json.loads(result_json)
    for _container_name, container_result in result["containers"].items():
        if _nonexisting_image(container_result):
            _remove_user_default_value(container_result)
            _remove_cmd_default_value(container_result)

    result_json = json.dumps(result)
    return result_json


def _nonexisting_image(container_result):
    for entry in container_result:
        if entry["type"] == "non_existing_image":
            return True
    return False


def _remove_user_default_value(container_result):
    for n, entry in enumerate(container_result):
        if (
            entry["type"] == "not_equal"
            and entry["property"] == "user"
            and entry["value_spec"] == ""
        ):
            container_result.pop(n)


def _remove_cmd_default_value(container_result):
    for n, entry in enumerate(container_result):
        if (
            entry["type"] == "not_equal"
            and entry["property"] == "cmd"
            and entry["value_spec"] == []
        ):
            container_result.pop(n)


root.add_command(deploy_diff("diff"), name="diff")
