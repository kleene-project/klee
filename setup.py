from distutils.core import setup

setup(
    name="Klee",
    version="0.0.1",
    description="Command line interface to Kleened.",
    author="Lasse Grinderslev Andersen",
    author_email="lasse@philomath.dk",
    url="https://github.com/organisation/repo",
    packages=["klee"],
    entry_points={"console_scripts": ["klee=klee.main:cli"]},
)
