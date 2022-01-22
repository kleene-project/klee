from distutils.core import setup

setup(
    name="JCli",
    version="0.0.1",
    description="Command line interface to Jocker Engine.",
    author="Lasse Grinderslev Andersen",
    author_email="lasse@philomath.dk",
    url="https://github.com/organisation/repo",
    packages=["jcli"],
    entry_points={
        "console_scripts": ["jcli=jcli.main:cli"],
    },
)
