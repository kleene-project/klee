import json

import inspect
from gettext import gettext

import click
from click.core import HelpFormatter, Context


import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box

from .config import config

# from .richclick import RichGroup, RichCommand, RootGroup
from .docs_generator import DocsGroup, DocsCommand

console = Console()


def echo_bold(msg):
    if config.theme == "rich-cli":
        echo(f"[bold]{msg}[/bold]")

    elif config.theme == "click-cli":
        echo(msg)
    else:
        raise Exception("Should not happen")


def echo(msg, **kwargs):
    if config.theme == "rich-cli":
        console.print(msg, **kwargs)

    elif config.theme == "click-cli":
        console.print(msg, **kwargs)
    else:
        raise Exception("Should not happen")


def connection_closed_unexpectedly():
    console.print("ERROR! Connection closed unexpectedly.")


def unexpected_error():
    echo_bold("\nERROR! Some unexpected error occured")


def unrecognized_status_code(status_code):
    echo_bold(f"unrecognized status-code received from kleened: {status_code}")


def print_unable_to_connect(msg):
    echo_bold(f"unable to connect to kleened: {msg}")


def print_id_list(id_list):
    id_list = "\n".join(id_list)
    console.print(id_list)


def print_websocket_closing(msg, attributes):
    for attrib in attributes:
        echo_bold(msg[attrib])


def print_json(json_obj):
    console.print_json(json.dumps(json_obj.to_dict()))

    # from rich.pretty import pprint
    # pprint(json_obj)


def print_table(items, columns):
    table = Table(show_edge=False, box=box.SIMPLE)

    for column_name, kwargs in columns:
        table.add_column(column_name, **kwargs)

    for item in items:
        table.add_row(*item)

    console.print(table)


class RootGroup(click.Group):
    def format_options(self, ctx: Context, formatter: HelpFormatter) -> None:
        click.Command.format_options(self, ctx, formatter)
        self.format_shortcuts(ctx, formatter)
        self.format_commands(ctx, formatter)

    def format_shortcuts(self, ctx: Context, formatter: HelpFormatter) -> None:
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue

            if cmd.hidden:
                commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands) != 0:
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help_ = cmd.get_short_help_str(limit)
                rows.append((subcommand, help_))

            if rows:
                with formatter.section(gettext("Shortcuts")):
                    formatter.write_dl(rows)


class RichGroup(click.Group):
    def format_help(self, ctx, _formatter):
        print_usage_line(self, ctx)
        print_help_section(self)
        print_options_section(self, ctx)
        print_commands_section(self, ctx)
        if ctx.command_path == "klee":
            print_shortcuts_section(self)


class RichCommand(click.Command):
    """Override Clicks help with a Richer version."""

    def format_help(self, ctx, _formatter):
        print_usage_line(self, ctx)
        print_help_section(self)
        print_options_section(self, ctx)


def command_cls():
    if config.theme == "rich-cli":
        return RichCommand

    if config.theme == "click-cli":
        return click.Command

    if config.theme == "docs-generator":
        return DocsCommand

    raise Exception(f"cli theme '{config.theme}' not known")


def group_cls():
    if config.theme == "rich-cli":
        return RichGroup

    if config.theme == "click-cli":
        return click.Group

    if config.theme == "docs-generator":
        return DocsGroup

    raise Exception(f"cli theme '{config.theme}' not known")


def root_cls():
    if config.theme == "rich-cli":
        return RichGroup

    if config.theme == "click-cli":
        return RootGroup

    if config.theme == "docs-generator":
        return DocsGroup

    raise Exception(f"cli theme '{config.theme}' not known")


def print_shortcuts_section(self):
    commands_table = Table(highlight=True, box=None, show_header=False)

    # commands = []
    for name, command in self.commands.items():
        # Hidden commands are the shortcuts
        if command.hidden:
            # commands.append((name, command))
            cmd_help = command.get_short_help_str(limit=200)
            commands_table.add_row(f"[yellow]{name}[/yellow]", Markdown(cmd_help))

    console.print(
        Panel(
            commands_table,
            border_style="dim",
            title="Shortcuts",
            style="bold",
            title_align="left",
        )
    )


def print_commands_section(self, ctx):
    commands_table = Table(highlight=True, box=None, show_header=False)

    commands = []
    for subcommand in self.list_commands(ctx):
        cmd = self.get_command(ctx, subcommand)
        # What is this, the tool lied about a command.  Ignore it
        if cmd is None:
            continue
        if cmd.hidden:
            continue

        commands.append((subcommand, cmd))

    for subcommand, cmd in commands:
        cmd_help = Markdown(cmd.get_short_help_str(limit=200))
        subcommand = f"[green]{subcommand}[/green]"
        commands_table.add_row(subcommand, cmd_help)

    console.print(
        Panel(
            commands_table,
            border_style="dim",
            title="Commands",
            style="bold",
            title_align="left",
        )
    )


def print_usage_line(self, ctx):
    pieces = []
    pieces.append(f"[b]{ctx.command_path}[/b]")
    for piece in self.collect_usage_pieces(ctx):
        pieces.append(f"[b]{piece}[/b]")

    console.print("Usage: " + " ".join(pieces))


from rich.markdown import Markdown


def print_help_section(self):
    if self.help is not None:
        # truncate the help text to the first form feed
        # text = inspect.cleandoc(self.help).partition("\f")[0]
        text = inspect.cleandoc(self.help)
    else:
        text = ""

    if text:
        help_table = Table(highlight=True, box=None, show_header=False, padding=(1, 2))
        help_table.add_row(Markdown(text))
        console.print(help_table)


def print_options_section(self, ctx):
    # Building options section
    options_table = Table(highlight=True, box=None, show_header=False)

    for param in self.get_params(ctx):

        if param.opts[0][:2] != "--":
            continue

        if len(param.opts) == 2:
            opt1 = f"[green]{param.opts[1]}[/green]"
            opt2 = f"[cyan]{param.opts[0]}[/cyan]"
        else:
            opt2 = f"[cyan]{param.opts[0]}[/cyan]"
            opt1 = ""

        if param.metavar:
            opt2 += f" [bold yellow]{param.metavar}[/bold yellow]"

        help_record = param.get_help_record(ctx)
        if help_record is None:
            help_ = ""
        else:
            help_ = param.get_help_record(ctx)[-1]

        options_table.add_row(opt1, opt2, Markdown(help_))

    console.print(
        Panel(
            options_table,
            border_style="dim",
            title="Options",
            style="bold",
            title_align="left",
        )
    )
