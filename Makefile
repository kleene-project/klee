# Path to kleened's minimal test-jail tarball. Override on the command line if your
# kleened checkout lives elsewhere:
#     make test KLEENED_MINIMAL_TESTJAIL=/path/to/minimal_testjail.txz
KLEENED_MINIMAL_TESTJAIL ?= $(HOME)/kleened/test/data/minimal_testjail.txz

# The tests need root: jails, ZFS and the daemon socket.
#
# sudo is given the venv's pytest by absolute path, because it resets PATH via
# secure_path and would otherwise pick up root's system pytest instead of the
# locked one. The path is resolved in the recipe rather than with GNU make's
# $(shell ...): FreeBSD's make is bmake, which has no such function.
#
# 'sudo env VAR=...' rather than 'sudo -E': -E depends on the sudoers SETENV
# privilege and still leaves PATH subject to secure_path.
test:
	sudo env KLEENED_MINIMAL_TESTJAIL="$(KLEENED_MINIMAL_TESTJAIL)" \
	    "$$(poetry env info --path)/bin/pytest" -x -vv

# The fast tier: no root, no kleened, no jails, no ZFS. Runs unprivileged in a
# couple of seconds, so it needs neither sudo nor the env var above.
#
# Collection is scoped to test/unit rather than relying on '-m unit' alone: pytest
# imports every collected module before applying marker filters, and the system
# tests fail at import when KLEENED_MINIMAL_TESTJAIL is unset. The marker is kept
# as a guard against a non-unit test being dropped into that directory.
test-unit:
	poetry run pytest -m unit -vv test/unit

# Output directory for the generated CLI reference pages. Override on the
# command line if the kleene-docs checkout lives elsewhere:
#     make docs KLEENE_DOCS=/path/to/kleene-docs
KLEENE_DOCS ?= $(HOME)/kleene_dev/kleene-docs

docs:
	poetry run python scripts/generate_yaml_docs.py $(KLEENE_DOCS)/data/klee-reference

.PHONY: test test-unit docs
