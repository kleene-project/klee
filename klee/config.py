import click

from .richclick import RichGroup, RichCommand
from .docs_generator import DocsGroup, DocsCommand


class ConfigSingleton:
    host = None
    tlsverify = None
    tlscert = None
    tlskey = None
    tlscacert = None
    cli_type = None

    @property
    def command_cls(self):
        if self.cli_type == "rich-cli":
            return RichCommand

        if self.cli_type == "click-cli":
            return click.Command

        if self.cli_type == "docs-generator":
            return DocsCommand

        raise Exception(f"CLI-type '{self.cli_type}' not known")

    @property
    def group_cls(self):
        if self.cli_type == "rich-cli":
            return RichGroup

        if self.cli_type == "click-cli":
            return click.Group

        if self.cli_type == "docs-generator":
            return DocsGroup

        raise Exception(f"CLI-type '{self.cli_type}' not known")

    def httpx_tls_kwargs(self):
        return {"verify": self.tlsverify, "cert": (self.tlscert, self.tlskey)}


config = ConfigSingleton()
