import oyaml as yaml

def main():
    with open("datasets.yaml", 'r') as f:
        datasets = yaml.safe_load(f)["datasets"]

    new_configs = {}
    for dataset in datasets:
        for path in dataset["files"]:
            new_configs[path] = {
                "name": dataset["name"].split("_ext")[0],
                "parent": dataset["parent"],
                "isdata": dataset["isdata"],
                "xsection": dataset["xsection"],
            }

    with open("paths.yaml", 'w') as f:
        yaml.dump(new_configs, f, indent=4)


if __name__ == "__main__":
    main()
