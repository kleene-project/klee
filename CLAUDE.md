# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Klee is the Python CLI for **Kleene**, a FreeBSD container manager. It is a Click app that talks to the
`kleened` daemon over HTTP (Unix socket by default: `http:///var/run/kleened.sock`) and WebSockets.

This repo is normally checked out as a subdirectory of the `kleene_dev` environment repo and shared into a
FreeBSD VM at `/vagrant/klee` (see the parent `CLAUDE.md`). Anything that touches jails, ZFS or a running
kleened must run inside that VM; editing, linting and the unit tier work fine on the host.

## Commands

```bash
# Fast tier: pure functions only, no root/kleened/jails/ZFS. Runs anywhere in seconds.
make test-unit

# Full system suite: needs root, a running kleened, and the minimal test-jail tarball.
make test
make test KLEENED_MINIMAL_TESTJAIL=/path/to/minimal_testjail.txz

# A single system test file / test
sudo env KLEENED_MINIMAL_TESTJAIL="$KLEENED_MINIMAL_TESTJAIL" \
    "$(poetry env info --path)/bin/pytest" -x -vv test/container_test.py
    # ... -k test_name  to narrow further

# Regenerate the reference docs YAML consumed by kleene-docs
make docs

# Regenerate klee/client from kleened's OpenAPI spec (target lives in the parent repo's Makefile.vagrant)
make update-klee-openapi
```

Test invocation gotchas encoded in the `Makefile` — preserve them if you touch it:

- `sudo` is handed the venv's pytest **by absolute path**, because `secure_path` resets `PATH` and root's
  system pytest would win otherwise.
- `sudo env VAR=...` rather than `sudo -E`, which needs the sudoers `SETENV` privilege.
- `test-unit` scopes collection to `test/unit` and not just `-m unit`: pytest imports every collected module
  before applying marker filters, and the system tests fail at import when `KLEENED_MINIMAL_TESTJAIL` is unset.
- The `Makefile` must stay bmake-compatible (FreeBSD make) — no `$(shell ...)`.

Test files are named `<thing>_test.py`, not `test_<thing>.py` (`python_files` in `pyproject.toml`).

## Architecture

### Command factory pattern

Every command is a **factory function**, not a decorated module-level object:

```python
def container_list(name, hidden=False):
    @click.command(cls=command_cls(), name=name, hidden=hidden)
    def listing(**kwargs): ...
    return listing
```

This exists so the same command can be instantiated twice under different names: once as a subcommand
(`klee container ls`) and once as a hidden top-level shortcut (`klee lsc`). `klee/shortcuts.py` holds the
shortcut → source-command map; `klee/root.py:create_cli()` builds both sets and registers them.
Shared option sets live in `klee/options.py` and are appended via `cmd.params.extend(...)`; `image build`
reuses the container-create options minus the irrelevant ones.

### Themes decide the Click classes — so import order matters

`config.theme` (`fancy` / `simple` / `docs-generator`) selects which Click class a command is built from, via
`command_cls()` / `group_cls()` / `root_cls()` in `klee/printing.py`. `fancy` uses the rich-rendering
subclasses, `docs-generator` uses `DocsGroup` / `DocsCommand` from `klee/docs_generator.py`, which capture
help metadata instead of printing it.

Because the class is chosen **at decoration time**, `create_cli()` loads config first and only then imports the
command modules. Keep those imports inside `create_cli()`; hoisting them to module scope silently locks in the
default theme. `scripts/generate_yaml_docs.py` relies on the same ordering: it sets the theme before importing
`klee.root`.

### Request flow

`klee/client/` is **generated** from kleened's OpenAPI spec by `openapi-python-client` — do not edit it by hand.
`klee/custom_client_templates/endpoint_module.py.jinja` customises the generator so every `sync_detailed`
endpoint takes an **httpx transport as its first positional argument**, which is what lets `klee/connection.py`
supply a Unix-socket transport.

Regular commands go through one helper:

```python
request_and_print_response(
    endpoint,                      # generated client function
    kwargs={...},                  # its parameters
    statuscode2printer={200: _print_container, 500: print_backend_error},
)
```

`klee/utils.py` owns that helper and turns httpx transport failures into user-facing messages plus `sys.exit`.
`klee/connection.py` builds the transport (uds vs. TCP, TLS material from config) for both HTTP and WebSockets.

### Streaming commands

`image build`, `image create`, `container exec` and `container run` stream over WebSockets
(`/images/build`, `/images/create`, `/exec/start`). The pattern: `create_websocket(endpoint)` async context
manager → send a JSON config frame → `listen_for_messages()` loops on `recv()` until the server closes, and the
**closing message is JSON in `websocket.close_reason`**, not a normal frame. Interactive exec additionally puts
the terminal in raw mode and pumps stdin through `loop.add_reader`.

### Config resolution

`klee/config.py` is a singleton with precedence: CLI flags > environment (`KLEE_*`) > config file
(`klee_config.yaml`, `~/.klee/`, `/usr/local/etc/klee/` on BSD). `root.py` bootstraps `--config`/`--theme` with
a bare `argparse` pass before Click runs, because both are needed to build the CLI itself. Note two existing
typos in the env-var table: `KLEE_TLS_CERT` maps to `tlscacert`, and `KLEE_TLS_KERY` is misspelt.

### Reference docs

`make docs` runs every command with `--help` under the `docs-generator` theme and dumps one YAML file per
command into `kleene-docs/_data/klee-reference` (the target hardcodes `/vagrant/kleene-docs`). The YAML merges
Click metadata with `docs/klee_<command>.md`, where a `## Description` section overrides the docstring and an
`## Examples` section is appended. Adding a command means adding the matching `docs/` file if it needs examples.

## Testing

Tests drive the CLI **in-process** through Click's `CliRunner` against a live kleened — not as a subprocess.
Consequences:

- The `config` singleton survives between invocations, so `testutils._invoke` clears it before each run.
- Helpers in `test/testutils.py` are the interface: `run(command, exit_code=0)` returns output as a list of
  lines for every command; `run_container()` and `remove_container()` decode the two commands whose output is
  worth parsing further; `listing_rows()` / `listing_ids()` parse rich-rendered tables (rows can wrap, so lines
  cannot simply be counted); `shell()` shells out to `jls`/`zfs` for host-side assertions.
- Fixtures in `test/conftest.py`: `create_testimage` (class-scoped `FreeBSD:latest` from the basejail dataset),
  `host_state` (asserts the ZFS dataset list is unchanged afterwards), `cleanup` (prunes containers, networks,
  volumes), and the combinations `testimage` / `testimage_and_cleanup`.
- `pytest-timeout` is on by default (`--timeout=300`) because held-open WebSockets can hang a run indefinitely.

New pure-function tests belong in `test/unit/` with `pytestmark = pytest.mark.unit`.
