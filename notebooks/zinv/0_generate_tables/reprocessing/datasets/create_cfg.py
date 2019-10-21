import re
import oyaml as yaml
import pysge

def get_nevents_sumweights(path, tree="Events", param="genWeight"):
    import ROOT
    rfile = ROOT.TFile.Open(path)
    rtree = rfile.Get(tree)

    if param is None:
        vals = int(rtree.GetEntries())
    else:
        rhist = ROOT.TH1D("h", "h", 1, 0, 2)
        rtree.Draw("1>>h", "genWeight")
        vals = (int(rtree.GetEntries()), float(rhist.GetBinContent(1)))
        del rhist
    del rtree
    del rfile
    return {path: vals}

def get_parent(das):
    return das.split("/")[1]

#runera_regex = re.compile("^/[a-zA-Z]+/Run(?P<runyear>[0-9]+)(?P<runletter>[A-Z]).*(?P<ver>(|ver[0-9])).*/(MINI|NANO)AOD$")
#def get_runera(das):
#    match = runera_regex.search(das)
#    if not match:
#        raise ValueError(f'No run era match to {das}')
#    runyear = int(match.group("runyear"))
#    runletter = match.group("runletter")
#    ver = match.group("ver")
#    ver = int(ver) if ver!="" else 1
#
#    return runyear, runletter, ver

#def create_name(parent, year, letter, ver):
#    return f'{parent}_Run{year}{letter}_v{ver}'

xrd_redir = "root://xrootd-cms.infn.it//"

def main():
    with open("data_v2.txt", 'r') as f:
        datain = f.read()

    datasets, tasks = [], []
    for block in datain.split("\n\n"):
        if len(block)==0:
            continue
        lines = block.split("\n")

        das = lines[1]
        files = sorted(list(set(lines[3].split(" "))))
        summary = eval(lines[5])[0]

        parent = get_parent(das)
        print(parent)
        #runyear, runletter, ver = get_runera(das)

        tasks.extend([{
            "task": get_nevents_sumweights,
            "args": (f'{xrd_redir}{p}',),
            "kwargs": {"param": None},
        } for p in files])

        isdata = True
        tree = "Events"
        xsec = None

        datasets.append({
            "name": parent,
            "parent": parent,
            "isdata": isdata,
            "nevents": int(summary["nevents"]),
            "sumweights": None,
            "files": [f'{xrd_redir}{f}' for f in files],
            "file_nevents": [],
            "DAS": das,
            "tree": tree,
            "xsection": xsec,
        })

    #results = pysge.local_submit(tasks)
    #results = pysge.mp_submit(tasks, 6)
    results = pysge.sge_submit(tasks, "dasq", "_ccsp_temp")

    all_files_results = {}
    for r in results:
        all_files_results.update(r)

    new_datasets = []
    for d in datasets:
        tot_nevts = 0
        tot_sumw = 0.
        fnevts = []
        for p in d["files"]:
            #nevts, sumw = all_files_results[p]
            nevts = all_files_results[p]
            sumw = nevts
            tot_nevts += nevts
            tot_sumw += sumw
            fnevts.append(nevts)
        if tot_nevts != d["nevents"]:
            print("Mismatch in nevents from files {} and summary {} for {}".format(
                tot_nevts, d["nevents"], d["DAS"],
            ))
        new_datasets.append({
            "name": d["name"],
            "parent": d["parent"],
            "isdata": d["isdata"],
            "nevents": tot_nevts,
            "sumweights": tot_sumw,
            "files": d["files"],
            "file_nevents": fnevts,
            "DAS": d["DAS"],
            "tree": d["tree"],
            "xsection": d["xsection"],
        })

    with open("data_v2.yaml", 'w') as f:
        yaml.dump(new_datasets, f, indent=4)

if __name__ == "__main__":
    main()
