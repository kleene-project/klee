test:
	pipenv run sudo pytest -x -vv

generate-spec:
	cd /host/kleened && sudo mix openapi.spec.json --spec Kleened.API.Spec

.PHONY: test
