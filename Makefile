# Path to kleened's minimal test-jail tarball. Override on the command line if your
# kleened checkout lives elsewhere:
#     make test KLEENED_MINIMAL_TESTJAIL=/path/to/minimal_testjail.txz
KLEENED_MINIMAL_TESTJAIL ?= $(HOME)/kleened/test/data/minimal_testjail.txz

# The tests need root (jails, ZFS, the daemon socket), but 'poetry run sudo pytest'
# does not do what it looks like: sudo resets PATH via secure_path, so the pytest
# that actually runs is root's system pytest rather than the locked venv one.
# Resolve the venv's pytest and hand sudo the absolute path.
#
# NB: the substitution happens in the *recipe*, not via GNU make's $(shell ...) --
# FreeBSD's make is bmake, which has no such function. '$$' survives both.
#
# 'sudo env VAR=...' rather than 'sudo -E': -E depends on the sudoers SETENV
# privilege and still leaves PATH subject to secure_path. Being explicit about the
# one variable the suite needs is predictable everywhere.
test:
	sudo env KLEENED_MINIMAL_TESTJAIL="$(KLEENED_MINIMAL_TESTJAIL)" \
	    "$$(poetry env info --path)/bin/pytest" -x -vv

docs:
	poetry run python scripts/generate_yaml_docs.py /vagrant/kleene-docs/_data/klee-reference

generate-spec:
	cd /vagrant/kleened && sudo mix openapi.spec.json --spec Kleened.API.Spec

.PHONY: test docs generate-spec
