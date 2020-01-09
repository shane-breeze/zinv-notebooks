import subprocess as sp
import shlex
import pysge
import oyaml as yaml

def parse_args():
    class Arguments:
        infile = "datasets.txt"
    return Arguments()

def run_command(cmd):
    p = sp.Popen(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.PIPE)
    return p.communicate()

def get_file_list(path):
    with open(path, 'r') as f:
        dataset_list = f.read().splitlines()

    with open("das_to_name.yaml", 'r') as f:
        cfg_ref = yaml.full_load(f)

    file_list = []
    print("get file list")
    for dataset in dataset_list:
        print(dataset)
        out, err = run_command("dasgoclient --query 'file dataset={}'".format(dataset))
        file_list.append({
            "name": cfg_ref["das_to_name"][dataset],
            "parent": cfg_ref["das_to_parent"][dataset],
            "isdata": "SIM" not in dataset.split("/")[3],
            "files": [f for f in out.decode('utf-8').splitlines()],
            "DAS": dataset,
            "tree": "Events",
            "xsection": cfg_ref["das_to_xsection"][dataset],
        })
    return file_list

def job(path, isdata=True):
    import uproot
    fullpath = "root://gfe02.grid.hep.ph.ic.ac.uk:1097" + path
    try:
        tree = uproot.open(fullpath)["Events"]
    except OSError as e:
        try:
            fullpath = "/vols/cms/sdb15/NanoAOD" + path
            tree = uproot.open(fullpath)["Events"]
        except OSError as e:
            return path, 0, 0., False

    nevents = int(tree.numentries)
    sumweights = float(nevents)
    if not isdata:
        sumweights = float(tree.array("genWeight").sum())
    return fullpath, nevents, sumweights, True

def create_tasks(cfgs):
    tasks = []
    print("create tasks")
    for cfg in cfgs:
        print(cfg["name"])
        for path in cfg["files"]:
            tasks.append({
                "task": job,
                "args": [path],
                "kwargs": { "isdata": cfg["isdata"], },
            })
    return tasks

def process_results(cfgs, results):
    idx = 0
    new_cfgs = []
    print("process results")
    for cfg in cfgs:
        print(cfg["name"])
        total_nevents = 0
        total_sumweights = 0.
        nevents_list = []
        fullpaths = []
        for path in cfg["files"]:
            fullpath, nevents, sumweights, success = results[idx]
            if not success:
                print("Failed {}".format(fullpath))
            total_nevents += nevents
            total_sumweights += sumweights
            nevents_list.append(nevents)
            fullpaths.append(fullpath)
            idx += 1
        new_cfgs.append({
            "name": str(cfg["name"]),
            "parent": str(cfg["parent"]),
            "isdata": bool(cfg["isdata"]),
            "nevents": int(total_nevents),
            "sumweights": float(total_sumweights),
            "files": [str(p) for p in fullpaths],
            "file_nevents": [int(n) for n in nevents_list],
            "DAS": str(cfg["DAS"]),
            "tree": str(cfg["tree"]),
            "xsection": float(cfg["xsection"]) if cfg["xsection"] is not None else None,
        })
    return new_cfgs

def main():
    options = parse_args()
    cfgs = get_file_list(options.infile)
    tasks = create_tasks(cfgs)
    #results = pysge.sge_submit(
    #    tasks, "xrdquery", "_ccsp_temp",
    #    options="-q hep.q -l h_rt=3:0:0 -l h_vmem=12G",
    #    dill_kw={'recurse': False},
    #)
    results = pysge.sge_resume(
        "xrdquery",
        "/vols/build/cms/sdb15/phd/ZinvWidth/zinv-notebooks/notebooks/zinv/0_generate_tables/configs_multitables/datasets/_ccsp_temp/tpd_20200109_171855_al77vxdo/",
    )

    new_cfgs = process_results(cfgs, results)

    with open("datasets.yaml", 'w') as f:
        yaml.dump(new_cfgs, f)

if __name__ == "__main__":
    main()
