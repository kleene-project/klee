import argparse
import os

import yaml

from click.testing import CliRunner
from klee.config import config

config.cli_type = "docs-generator"

# pylint: disable=wrong-import-position
from klee.root import create_cli
from klee.docs_generator import DocsGroup, DocsCommand


def iter_commands(cli):
    for cmd, obj in cli.commands.items():
        if isinstance(obj, DocsGroup):
            yield [cmd], obj
            for child_cmd, child_obj in iter_commands(obj):
                yield [cmd] + child_cmd, child_obj

        elif isinstance(obj, DocsCommand):
            yield [cmd], obj

        else:
            print("This should not happen")


def save_file(yaml_data, filename):
    with open(os.path.join(args.outdir, filename), "w", encoding="utf8") as f:
        f.write(yaml_data)


def create_yaml_data(cmd, obj):
    # # Use this if debugging Klee:
    # output = runner.invoke(cli, cmd + ["--help"])
    # print("Output from Klee:", output.stdout)
    runner.invoke(cli, cmd + ["--help"])
    return yaml.dump(obj.docs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="generate-docs",
        description="Generate YAML-files for Kleenes reference documentation",
    )
    parser.add_argument(
        "outdir", help="Path to a directory where the generated files should be stored."
    )
    args = parser.parse_args()
    runner = CliRunner()
    cli = create_cli()
    yaml_data = create_yaml_data([], cli)
    save_file(yaml_data, "klee.yaml")

    for cmd, obj in iter_commands(cli):
        print("Running: ", cmd, obj)
        yaml_data = create_yaml_data(cmd, obj)
        filename = "_".join(["klee"] + cmd) + ".yaml"
        save_file(yaml_data, filename)
