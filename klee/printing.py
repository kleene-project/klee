import json
import inspect
from gettext import gettext

import click
from click.core import HelpFormatter, Context

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.markup import escape
from rich import box


from .config import config

from .docs_generator import DocsGroup, DocsCommand

console = Console()

THEME_FANCY = "fancy"
THEME_SIMPLE = "simple"
THEME_DOCSGENERATOR = "docs-generator"


def echo_bold(msg):
    style = None

    if config.theme == THEME_FANCY:
        style = "bold"

    console.print(msg, style=style)


def echo(msg, newline=True):
    click.echo(msg, nl=newline)


def echo_error(msg):
    style = None

    if config.theme == THEME_FANCY:
        style = "bold red"

    console.print(escape(msg), style=style)


def connection_closed_unexpectedly():
    echo_error("ERROR! Connection closed unexpectedly.")


def unexpected_error():
    echo_error("\nERROR! Some unexpected error occured")


def unrecognized_status_code(status_code):
    echo_error(f"unrecognized status-code received from kleened: {status_code}")


def print_unable_to_connect(msg):
    echo_error(f"unable to connect to kleened: {msg}")


def print_timeout():
    echo_error("Error! Timed out while waiting for Kleene to respond.")


def print_unexpected_response():
    echo_error("Error! Unexpected response received from Kleened.")


def print_nothing(_response):
    pass


def print_response_id(response):
    echo_bold(response.parsed.id)


def print_response_msg(response):
    echo_bold(response.parsed.message)


def print_backend_error(_response):
    echo_bold("unknown backend error")


def print_id_list(response):
    id_list = "\n".join(response.parsed)
    echo_bold(id_list)


def print_websocket_closing(msg, attributes):
    for attrib in attributes:
        echo_bold(msg[attrib])


def print_json(response):
    if config.theme == THEME_FANCY:
        console.print_json(json.dumps(response.parsed.to_dict()))

    elif config.theme == THEME_SIMPLE:
        click.echo(json.dumps(response.parsed.to_dict(), indent=2))

    # # OpenAPI-spec printing
    # from rich.pretty import pprint
    # pprint(response.parsed)


def print_image_column(name, tag, id_):
    if name == "":
        return f"[b bright_magenta]{id_}[/b bright_magenta]"
    return f"[b bright_blue]{name}:[/b bright_blue][bright_cyan]{tag}[/bright_cyan]"


def is_running_str(running):
    if config.theme == THEME_FANCY:
        if running:
            return "[green]running[/green]"
        return "[red]stopped[/red]"

    if running:
        return "running"
    return "stopped"


def print_table(items, columns):
    if config.theme == THEME_FANCY:
        table = Table(show_edge=False, box=box.SIMPLE)
    else:
        table = Table(show_edge=False, header_style=None, box=box.ASCII)

    for column_name, kwargs in columns:
        if config.theme == THEME_FANCY:
            table.add_column(column_name, **kwargs)
        elif config.theme == THEME_SIMPLE:
            if "style" in kwargs:
                kwargs.pop("style")
            table.add_column(column_name, **kwargs)

    for item in items:
        table.add_row(*item)

    console.print(table, soft_wrap=True)


class RootGroup(click.Group):
    def format_options(self, ctx: Context, formatter: HelpFormatter) -> None:
        click.Command.format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)
        self.format_shortcuts(ctx, formatter)

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
    if config.theme == THEME_FANCY:
        return RichCommand

    if config.theme == THEME_SIMPLE:
        return click.Command

    if config.theme == THEME_DOCSGENERATOR:
        return DocsCommand

    raise Exception(f"cli theme '{config.theme}' not known")


def group_cls():
    if config.theme == THEME_FANCY:
        return RichGroup

    if config.theme == THEME_SIMPLE:
        return click.Group

    if config.theme == THEME_DOCSGENERATOR:
        return DocsGroup

    raise Exception(f"cli theme '{config.theme}' not known")


def root_cls():
    if config.theme == THEME_FANCY:
        return RichGroup

    if config.theme == THEME_SIMPLE:
        return RootGroup

    if config.theme == THEME_DOCSGENERATOR:
        return DocsGroup

    raise Exception(f"cli theme '{config.theme}' not known")


SINGLE_SHORTCUTS = {"build", "create", "exec", "restart", "start", "stop", "run"}


def print_shortcuts_section(self):
    commands_table = Table(highlight=True, box=None, show_header=False)

    # commands = []
    for name, command in self.commands.items():
        # Hidden commands are the shortcuts
        if command.hidden and command.name in SINGLE_SHORTCUTS:
            cmd_help = command.get_short_help_str(limit=200)
            commands_table.add_row(Text(name, style="bold yellow"), Markdown(cmd_help))

    is_help = (
        "Inspect an object, where X is [c]ontainer, [i]mage, [n]etwork, or [v]olume."
    )
    rm_help = "Remove one or more objects, where X is [c]ontainer, [i]mage, [n]etwork, or [v]olume."
    ls_help = "List objects, where X is [c]ontainer, [i]mage, [n]etwork, or [v]olume."
    commands_table.add_row(Text("isX", style="bold yellow"), Markdown(is_help))
    commands_table.add_row(Text("rmX", style="bold yellow"), Markdown(rm_help))
    commands_table.add_row(Text("lsX", style="bold yellow"), Markdown(ls_help))
    console.print(
        Panel(commands_table, border_style="dim", title="Shortcuts", title_align="left")
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
        subcommand = Text(subcommand, style="bold green")
        commands_table.add_row(subcommand, cmd_help)

    console.print(
        Panel(commands_table, border_style="dim", title="Commands", title_align="left")
    )


def print_usage_line(self, ctx):
    pieces = []
    pieces.append(ctx.command_path)
    for piece in self.collect_usage_pieces(ctx):
        pieces.append(piece)

    console.print(Text("Usage: ") + Text(" ".join(pieces), style="bold"))


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


def no_formatting(text):
    return text


def print_options_section(self, ctx):
    # Building options section
    options_table = Table(highlight=True, box=None, show_header=False)
    style_opt = "bold cyan"
    style_opt_short = "bold green"
    style_metavar = "bold blue"

    for param in self.get_params(ctx):
        if param.opts[0][:2] != "--":
            continue

        if len(param.opts) == 2:
            opt1 = Text(param.opts[1], style=style_opt_short)
            opt2 = Text(param.opts[0], style=style_opt)
        else:
            opt2 = Text(param.opts[0], style=style_opt)
            opt1 = Text("", style=style_opt_short)

        if param.metavar:
            opt2 += Text(f" {param.metavar}", style=style_metavar)

        # If the '--dns/--no-dns' form of printing options is preferred, uncomment below:
        # if len(param.secondary_opts) > 0:
        #    opt2 = opt2 + "/" + param.secondary_opts[0]

        help_record = param.get_help_record(ctx)
        if help_record is None:
            help_ = ""
        else:
            help_ = param.get_help_record(ctx)[-1]

        options_table.add_row(opt1, opt2, Markdown(help_))

    console.print(
        Panel(options_table, border_style="dim", title="Options", title_align="left")
    )
