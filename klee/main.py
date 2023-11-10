from .config import config

# pylint: disable=wrong-import-position
from .root import create_cli


cli = create_cli()

if __name__ == "__main__":
    cli()
