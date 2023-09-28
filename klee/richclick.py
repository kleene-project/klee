import inspect

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


def print_table(items, columns):
    table = Table(show_edge=False, box=box.SIMPLE)

    for column_name, kwargs in columns:
        table.add_column(column_name, **kwargs)

    for item in items:
        table.add_row(*item)

    console.print(table)


class RichGroup(click.Group):
    def format_help(self, ctx, _formatter):
        highlighter = _create_highlighter()
        console = _create_help_console(highlighter)

        _print_usage_line(self, ctx, console)
        _print_help_section(self, console)
        _print_options_section(self, console, highlighter, ctx)
        _print_commands_section(self, console, highlighter, ctx)


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
