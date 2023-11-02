from gettext import gettext
import inspect

import click
from click.core import HelpFormatter, Context
from rich.console import Console
from rich.table import Table
from rich.text import Text

from rich import box


console = Console()


def print_id_list(id_list):
    id_list = " ".join(id_list)
    console.print(id_list)


def print_json(json_obj):
    import json

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
        highlighter = _create_highlighter()
        console = _create_help_console(highlighter)
        _print_usage_line(self, ctx, console)
        _print_help_section(self, console)
        _print_options_section(self, console, highlighter, ctx)
        _print_commands_section(self, console, highlighter, ctx)
        if ctx.command_path == "klee":
            _print_shortcuts_section(self, console, highlighter, ctx)


def _print_shortcuts_section(self, console, highlighter, ctx):
    from rich.panel import Panel

    commands_table = Table(highlight=True, box=None, show_header=False)

    commands = []
    for name, command in self.commands.items():
        # Hidden commands are the shortcuts
        if command.hidden:
            commands.append((name, command))
            cmd_help = command.get_short_help_str(limit=200)
            commands_table.add_row(name, highlighter(cmd_help))

    console.print(
        Panel(
            commands_table,
            border_style="dim",
            title="Shortcuts",
            style="bold",
            title_align="left",
        )
    )


def _print_commands_section(self, console, highlighter, ctx):
    from rich.panel import Panel

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
        cmd_help = cmd.get_short_help_str(limit=200)
        commands_table.add_row(subcommand, highlighter(cmd_help))

    console.print(
        Panel(
            commands_table,
            border_style="dim",
            title="Commands",
            style="bold",
            title_align="left",
        )
    )


class RichCommand(click.Command):
    """Override Clicks help with a Richer version."""

    def format_help(self, ctx, _formatter):
        highlighter = _create_highlighter()
        console = _create_help_console(highlighter)

        _print_usage_line(self, ctx, console)
        _print_help_section(self, console)
        _print_options_section(self, console, highlighter, ctx)


def _print_usage_line(self, ctx, console):
    pieces = []
    pieces.append(f"[b]{ctx.command_path}[/b]")
    for piece in self.collect_usage_pieces(ctx):
        pieces.append(f"[b]{piece}[/b]")

    console.print("Usage: " + " ".join(pieces))


def _print_help_section(self, console):
    if self.help is not None:
        # truncate the help text to the first form feed
        # text = inspect.cleandoc(self.help).partition("\f")[0]
        text = inspect.cleandoc(self.help)
    else:
        text = ""

    if text:
        from rich.markdown import Markdown

        help_table = Table(highlight=True, box=None, show_header=False, padding=(1, 2))
        help_table.add_row(Markdown(text))
        console.print(help_table)


def _print_options_section(self, console, highlighter, ctx):
    from rich.panel import Panel

    # Building options section
    options_table = Table(highlight=True, box=None, show_header=False)

    for param in self.get_params(ctx):

        if param.opts[0][:2] != "--":
            continue

        if len(param.opts) == 2:
            opt1 = highlighter(param.opts[1])
            opt2 = highlighter(param.opts[0])
        else:
            opt2 = highlighter(param.opts[0])
            opt1 = Text("")

        if param.metavar:
            opt2 += Text(f" {param.metavar}", style="bold yellow")

        help_record = param.get_help_record(ctx)
        if help_record is None:
            help_ = ""
        else:
            help_ = Text.from_markup(param.get_help_record(ctx)[-1], emoji=False)

        options_table.add_row(opt1, opt2, highlighter(help_))

    console.print(
        Panel(
            options_table,
            border_style="dim",
            title="Options",
            style="bold",
            title_align="left",
        )
    )


def _create_help_console(highlighter):
    from rich.theme import Theme

    console = Console(
        theme=Theme({"option": "bold cyan", "switch": "bold green"}),
        highlighter=highlighter,
    )
    return console


def _create_highlighter():
    from rich.highlighter import RegexHighlighter

    class OptionHighlighter(RegexHighlighter):
        highlights = [r"(?P<switch>\-\w)", r"(?P<option>\-\-[\w\-]+)"]

    return OptionHighlighter()
