## Generating reference documentation

Klee's reference documentation on the Kleene documentation website is generated from
annotations in the Klee source code. Generating the files for Klee's reference documentation
can be done by invoking a simple script:

```console
# Assuming you are in the klee repos and are using Poetry:
$ poetry shell
$ python scripts/generate_yaml_docs.py /path/to/kleene-docs/_data/klee-reference
... script output here ...
```

The script takes as a single argument the output directory where the generated YAML-files
should be stored. The location is the subdirectory `_data/klee-reference` in the Kleene
documentation repos, which is `/path/to/kleene-docs` in this example.

The generated YAML-files are compiled from two sources:

- The metadata specified using `click` (python package).
- Additional markdown files in `/docs`.

The additional markdown files can contain extra documentation in the form of a *example*
and/or a *description* section. The latter replaces the contribution from `click`'s
help-docs, if present.
