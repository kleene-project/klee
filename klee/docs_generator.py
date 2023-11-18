import os

import inspect

import click

from .shortcuts import SHORTCUTS


class DocsGroup(click.Group):
    docs = None

    def format_help(self, ctx, _formatter):
        self.docs = {
            "usage": _usage(self, ctx),
            "long": _long_help(self, ctx),
            "short": self.get_short_help_str(),
            "options": _options(self, ctx),
        }
        _examples(self.docs, ctx)
        _additional_fields(self.docs, ctx)
        cnames, clinks = _commands(self, ctx)
        self.docs["cname"] = cnames
        self.docs["clink"] = clinks


class DocsCommand(click.Command):
    docs = None

    def format_help(self, ctx, _formatter):
        self.docs = {
            "usage": _usage(self, ctx),
            "long": _long_help(self, ctx),
            "short": self.get_short_help_str(),
            "options": _options(self, ctx),
        }
        _shortcut(self.docs, ctx)
        _examples(self.docs, ctx)
        _additional_fields(self.docs, ctx)


def _commands(self, ctx):
    cnames = []
    clinks = []
    for subcommand, cmd in self.commands.items():
        # What is this, the tool lied about a command. Ignore it
        if cmd is None:
            continue

        if cmd.hidden:
            continue

        # cmd_help = cmd.get_short_help_str(limit=200)
        root_cmd = ctx.command_path
        cnames.append(f"{root_cmd} {subcommand}")

        root_cmd = root_cmd.replace(" ", "_")
        clinks.append(f"{root_cmd}_{subcommand}.yaml")
    return cnames, clinks


def _shortcut(docs, ctx):
    command_list = ctx.command_path.split(" ")
    # Remove the 'klee' root command:
    command = " ".join(command_list[1:])
    if command in SHORTCUTS:
        docs["shortcut"] = SHORTCUTS[command]


def _additional_fields(docs, ctx):
    command_list = ctx.command_path.split(" ")
    docs["command"] = ctx.command_path
    docs["deprecated"] = False
    docs["experimental"] = False
    docs["experimentalcli"] = False

    if len(command_list) != 1:
        parent_command = " ".join(command_list[:-1])
        docs["pname"] = parent_command
        docs["plink"] = parent_command.replace(" ", "_") + ".yaml"


def _usage(self, ctx):
    return ctx.command_path + " " + " ".join(self.collect_usage_pieces(ctx))


EXPERIMENTAL_OPTIONS = {"tty"}


def _options(self, ctx):
    options = []
    for param in self.get_params(ctx):
        # We're only interested in click.Options
        if isinstance(param, click.Argument):
            continue

        option = {"deprecated": False, "experimental": False, "experimentalcli": False}

        if param.human_readable_name in EXPERIMENTAL_OPTIONS:
            option.update({"experimental": True, "experimentalcli": True})

        # [2:] to avoid '--'
        option["option"] = param.opts[0][2:]
        if len(param.opts) == 2:
            # [1:] to avoid '-'
            option["shorthand"] = param.opts[1][1:]

        if param.metavar:
            option["value_type"] = param.metavar

        help_record = param.get_help_record(ctx)
        if help_record is not None:
            option["description"] = param.get_help_record(ctx)[-1]

        options.append(option)

    return options


def _long_help(self, ctx):
    command = _command(ctx)
    docs_file = _docs_file(command)

    if docs_file is not None:
        description, _ = _extract_sections_from_docsfile(docs_file)
        if description is not None:
            return description

    if self.help is not None:
        return inspect.cleandoc(self.help)

    return ""


def _examples(docs, ctx):
    command = _command(ctx)
    docs_file = _docs_file(command)

    if docs_file is not None:
        _description, examples = _extract_sections_from_docsfile(docs_file)
        if examples is not None:
            docs["examples"] = examples


def _command(ctx):
    command_list = ctx.command_path.split(" ")
    if len(command_list) == 2:
        potential_shortcut = command_list[1]
        if potential_shortcut in SHORTCUTS:
            source_command = SHORTCUTS[potential_shortcut]
            return f"klee {source_command}"

    return ctx.command_path


def _docs_file(command):
    docs_path = os.path.join(os.path.dirname(__file__), "../docs")
    docs_path = os.path.abspath(docs_path)
    command_docs_file = command.replace(" ", "_") + ".md"
    command_docs = os.path.join(docs_path, command_docs_file)
    try:
        with open(command_docs, "r", encoding="utf8") as f:
            return f.read()

    except FileNotFoundError:
        return None


def _extract_sections_from_docsfile(docsfile):
    description_mark = "## Description\n"
    examples_mark = "## Examples\n"
    description_start = docsfile.find(description_mark)
    examples_start = docsfile.find(examples_mark)
    description = None
    examples = None
    if description_start > -1:
        # The description subsection exists, check for examples and extract description subsection accordingly
        if examples_start > -1:
            description = docsfile[
                description_start + len(description_mark) : examples_start - 1
            ]
        else:
            description = docsfile[description_start + len(description_mark) :]

    if examples_start > -1:
        # The examples subsection exists, extract it
        examples = docsfile[examples_start + len(examples_mark) :]

    return description, examples
