import inspect

import click


class DocsGroup(click.Group):
    docs = None

    def format_help(self, ctx, _formatter):
        self.docs = {
            "usage": _usage(self, ctx),
            "long": _long_help(self),
            "short": _short_help(self),
            "options": _options(self, ctx),
        }
        _additional_fields(self.docs, ctx)
        cnames, clinks = _commands(self, ctx)
        self.docs["cnames"] = cnames
        self.docs["clinks"] = clinks


class DocsCommand(click.Command):
    docs = None

    def format_help(self, ctx, _formatter):
        self.docs = {
            "usage": _usage(self, ctx),
            "long": _long_help(self),
            "short": _short_help(self),
            "options": _options(self, ctx),
        }
        _additional_fields(self.docs, ctx)


def _short_help(self):
    return self.get_short_help_str()


def _commands(self, ctx):
    cnames = []
    clinks = []
    cname_template = "{root_cmd} {subcmd}"
    clink_template = "klee_{root_cmd}_{subcmd}.yaml"
    for subcommand, cmd in self.commands.items():
        # What is this, the tool lied about a command. Ignore it
        if cmd is None:
            continue

        if cmd.hidden:
            continue

        # cmd_help = cmd.get_short_help_str(limit=200)
        root_cmd = ctx.command_path
        cnames.append(cname_template.format(root_cmd=root_cmd, subcmd=subcommand))
        clinks.append(clink_template.format(root_cmd=root_cmd[5:], subcmd=subcommand))
    return cnames, clinks


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


def _long_help(self):
    if self.help is not None:
        return inspect.cleandoc(self.help)
    return ""


def _options(self, ctx):
    options = []
    for param in self.get_params(ctx):
        option = {"deprecated": False, "experimental": False, "experimentalcli": False}
        # We're only interested in click.Options
        if isinstance(param, click.Argument):
            continue

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
