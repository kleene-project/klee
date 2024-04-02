test:
	poetry run sudo pytest -x -vv

docs:
	poetry run python scripts/generate_yaml_docs.py /host/kleene-docs/_data/engine-cli

generate-spec:
	cd /host/kleened && sudo mix openapi.spec.json --spec Kleened.API.Spec

.PHONY: test
