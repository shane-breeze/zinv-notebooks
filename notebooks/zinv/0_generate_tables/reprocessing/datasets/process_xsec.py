import oyaml as yaml

with open("mc_v2.yaml", "r") as f:
    cfg_in = yaml.full_load(f)

with open("ref.yaml", 'r') as f:
    cfg_ref = yaml.full_load(f)["datasets"]

new_cfg_in = []
for d in cfg_in:
    if d["name"] not in cfg_ref:
        print("Can't find {}".format(d["name"]))
        xsec = 0.
    else:
        xsec = cfg_ref[d["name"]]["xsection"]
    new_cfg_in.append({
        "name": d["name"],
        "parent": d["parent"],
        "isdata": d["isdata"],
        "nevents": d["nevents"],
        "sumweights": d["sumweights"],
        "files": d["files"],
        "file_nevents": d["file_nevents"],
        "DAS": d["DAS"],
        "tree": d["tree"],
        "xsection": xsec,
    })

cfg_out = {
    "default": {"energy": 13000, "lumi": 35860},
    "datasets": new_cfg_in,
}

with open("mc_v3.yaml", 'w') as f:
    yaml.dump(cfg_out, f, indent=4)

