import os
import sys

# from urllib.parse import urlparse

import yaml
import click

from .richclick import RichGroup, RichCommand, RootGroup
from .docs_generator import DocsGroup, DocsCommand

ERROR_INVALID_CONFIG = (
    "Error! Config file {filepath} is not valid: parameter name '{parameter}' unknown"
)


def create_file_locations():
    file_locations = ["klee_config.yaml"]
    if "linux" in sys.platform:
        file_locations.append("~/.klee/klee_config.yaml")
        file_locations.append("/etc/klee/klee_config.yaml")

    elif "bsd" in sys.platform:
        file_locations.append("~/.klee/klee_config.yaml")
        file_locations.append("/usr/local/etc/klee/klee_config.yaml")
    return file_locations


class ConfigSingleton:
    host = None
    tlsverify = None
    tlscert = None
    tlskey = None
    tlscacert = None
    theme = "rich-cli"
    # theme = "click-cli"

    config_filepath = None
    config_file = None
    invalid_param = None
    _config_params = ["host", "tlsverify", "tlscert", "tlskey", "tlscacert", "theme"]

    def load_config(self, ctx):
        # To be sure, we clean the configuration parameters, because
        # during testing the config singleton object persists across several CLI invocations
        for param in self._config_params:
            if param == "theme":
                continue

            setattr(self, param, None)

        if not self._load_configuration_files():
            filepath = config.config_filepath
            param = config.invalid_param
            msg = ERROR_INVALID_CONFIG.format(filepath=filepath, parameter=param)
            click.echo(msg)
            ctx.exit(code=-1)

    @property
    def command_cls(self):
        if self.theme == "rich-cli":
            return RichCommand

        if self.theme == "click-cli":
            return click.Command

        if self.theme == "docs-generator":
            return DocsCommand

        raise Exception(f"CLI-type '{self.theme}' not known")

    @property
    def group_cls(self):
        if self.theme == "rich-cli":
            return RichGroup

        if self.theme == "click-cli":
            return click.Group

        if self.theme == "docs-generator":
            return DocsGroup

        raise Exception(f"CLI-type '{self.theme}' not known")

    @property
    def root_cls(self):
        if self.theme == "rich-cli":
            return RichGroup

        if self.theme == "click-cli":
            return RootGroup

        if self.theme == "docs-generator":
            return DocsGroup

        raise Exception(f"Klee console theme '{self.theme}' not known")

    def httpx_tls_kwargs(self):
        return {"verify": self.tlsverify, "cert": (self.tlscert, self.tlskey)}

    def _load_configuration_files(self):
        if not self._find_config_file():
            return True

        self.invalid_param = self._unknown_parameter()
        if self.invalid_param is not None:
            return False

        for key, value in self.config_file.items():
            setattr(self, key, value)

        return True

    def _find_config_file(self):
        for filepath in create_file_locations():
            # In case of the '~/' directory
            filepath = os.path.expanduser(filepath)

            try:
                with open(filepath, "r", encoding="utf8") as f:
                    data = f.read()
            except FileNotFoundError:
                continue

            try:
                config = yaml.safe_load(data)
            except yaml.parser.ParserError:
                click.echo(f"Error! Could not parse config at {filepath}")
                continue

            self.config_filepath = filepath
            self.config_file = config
            return True

        return False

    def _unknown_parameter(self):
        parameters = set(self._config_params)
        for parameter in self.config_file.keys():
            if parameter not in parameters:
                return parameter

        return None


config = ConfigSingleton()
