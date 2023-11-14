import os
import sys

import yaml
import click


def create_default_config_locations():
    locations = ["klee_config.yaml"]

    if "linux" in sys.platform:
        locations.append("~/.klee/klee_config.yaml")
        locations.append("/etc/klee/klee_config.yaml")

    elif "bsd" in sys.platform:
        locations.append("~/.klee/klee_config.yaml")
        locations.append("/usr/local/etc/klee/klee_config.yaml")

    return locations


class ConfigSingleton:
    host = None
    tlsverify = None
    tlscert = None
    tlskey = None
    tlscacert = None
    theme = "fancy"

    config_filepath = None
    invalid_file = None
    invalid_param = None
    _config_file = None
    _config_params = ["host", "tlsverify", "tlscert", "tlskey", "tlscacert", "theme"]
    _environment_params = {
        "KLEE_CONFIG": "config_filepath",
        "KLEE_THEME": "theme",
        "KLEE_HOST": "host",
        "KLEE_TLS_VERIFY": "tlsverify",
        "KLEE_TLS_CERT": "tlscacert",
        "KLEE_TLS_KERY": "tlskey",
        "KLEE_TLS_CACERT": "tlscacert",
    }

    def load_environment_variables(self):
        klee_variables = set(self._environment_params.keys())
        for varname, value in os.environ.items():
            if varname in klee_variables:
                config_param = self._environment_params[varname]
                if config_param == "tlsverify":
                    value = True if value.lower() == "true" else False
                    setattr(self, config_param, True)

                setattr(self, config_param, value)

    def update_bootstrap_options(self, config_filepath, theme):
        if config_filepath is not None:
            self.config_filepath = config_filepath

        if theme is not None:
            self.theme = theme

    def load_config_file(self):
        config_loaded = self._find_and_load_config_file()

        if config_loaded is False:
            # No valid config file found. No more to do.
            return

        self.invalid_param = self._unknown_parameter()
        if self.invalid_param is not None:
            self.invalid_file = True
            return

        for key, value in self._config_file.items():
            # Check if the attribute have been previously set by environment variables/CLI args
            if getattr(self, key) is None:
                setattr(self, key, value)

    def _find_and_load_config_file(self):
        for filepath in self.file_locations():
            # In case of the '~/' directory:
            filepath = os.path.expanduser(filepath)

            try:
                with open(filepath, "r", encoding="utf8") as f:
                    data = f.read()

                config = yaml.safe_load(data)

            except FileNotFoundError:
                continue

            except yaml.parser.ParserError:
                click.echo(f"Error! Could not parse config at {filepath}")
                continue

            self.config_filepath = filepath
            self._config_file = config

            return True

        return False

    def file_locations(self):
        # Try to see if a config_filepath have been supplied by environment variables/CLI args
        if self.config_filepath is not None:
            return [self.config_filepath]

        return create_default_config_locations()

    def _unknown_parameter(self):
        parameters = set(self._config_params)
        for parameter in self._config_file.keys():
            if parameter not in parameters:
                return parameter

        return None

    def httpx_tls_kwargs(self):
        return {"verify": self.tlsverify, "cert": (self.tlscert, self.tlskey)}


config = ConfigSingleton()
