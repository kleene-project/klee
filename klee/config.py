import os
import sys

# from urllib.parse import urlparse

import yaml
import click


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
    invalid_file = None
    invalid_param = None
    _config_file = None
    _config_params = ["host", "tlsverify", "tlscert", "tlskey", "tlscacert", "theme"]

    def load_config(self):
        if not self._find_config_file():
            return

        self.invalid_param = self._unknown_parameter()
        if self.invalid_param is not None:
            self.invalid_file = True
            return

        for key, value in self._config_file.items():
            setattr(self, key, value)

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
            self._config_file = config
            return True

        return False

    def _unknown_parameter(self):
        parameters = set(self._config_params)
        for parameter in self._config_file.keys():
            if parameter not in parameters:
                return parameter

        return None

    def httpx_tls_kwargs(self):
        return {"verify": self.tlsverify, "cert": (self.tlscert, self.tlskey)}


config = ConfigSingleton()
