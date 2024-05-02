test:
	poetry run sudo pytest -x -vv

docs:
	poetry run python scripts/generate_yaml_docs.py /vagrant/kleene-docs/_data/klee-reference

generate-spec:
	cd /vagrant/kleened && sudo mix openapi.spec.json --spec Kleened.API.Spec

.PHONY: test docs generate-spec
