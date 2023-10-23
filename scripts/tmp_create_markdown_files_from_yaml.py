from os import listdir
from os.path import join
import yaml

INPUT_DIR = "/host/kleene-docs/_data/engine-cli"
OUTPUT_DIR = "/host/klee/docs"


def generate_markdown():
    for path in listdir(INPUT_DIR):
        print(f"processing: {path}")
        with open(join(INPUT_DIR, path), "r") as f:
            lines = "".join(f.readlines())
        spec = yaml.load(lines, yaml.Loader)
        output_basename = f"klee{path[6:-5]}"

        output_file = join(OUTPUT_DIR, output_basename + ".md")
        f = None

        if spec["long"] != spec["short"]:
            f = open(output_file, "w")
            # diff = len(spec["long"]) - len(spec["short"])
            # print(f"short and long differ by {diff} characters")
            f.write("## Description\n")
            f.write(spec["long"])
            f.write("\n\n")

        if "examples" in spec:
            if f is None:
                f = open(output_file, "w")
            f.write("## Examples\n")
            f.write(spec["examples"])

        if f is not None:
            f.close()


if __name__ == "__main__":
    generate_markdown()
