from .config import config

# config.cli_type = "rich-cli"
config.cli_type = "click-cli"

# pylint: disable=wrong-import-position
from .root import create_cli


cli = create_cli()

if __name__ == "__main__":
    cli()
