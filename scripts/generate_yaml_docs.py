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


def create_yaml_data(cmd, obj):
    runner.invoke(cli, cmd + ["--help"])
    return yaml.dump(obj.docs)


if __name__ == "__main__":
    runner = CliRunner()
    cli = create_cli()
    for cmd, obj in iter_commands(cli):
        if cmd == ["image", "build"]:  # , "create"]:
            # cmd.append("--help")
            print("Running: ", cmd, obj, "\n")
            yaml_data = create_yaml_data(cmd, obj)
            filename = "_".join(["klee"] + cmd) + ".yaml"
            print(yaml_data)
            with open(filename, "w", encoding="utf8") as f:
                f.write(yaml_data)
            break
