import re
import ROOT
import oyaml as yaml

def get_nevents(path, tree="Events"):
    rfile = ROOT.TFile.Open(path, "READ")
    rtree = rfile.Get(tree)
    return rtree.GetEntries()

def get_parent(das):
    return das.split("/")[1]

runera_regex = re.compile("^/[a-zA-Z]+/Run(?P<runyear>[0-9]+)(?P<runletter>[A-Z]).*(?P<ver>(|ver[0-9])).*/(MINI|NANO)AOD$")
def get_runera(das):
    match = runera_regex.search(das)
    if not match:
        raise ValueError(f'No run era match to {das}')
    runyear = int(match.group("runyear"))
    runletter = match.group("runletter")
    ver = match.group("ver")
    ver = int(ver) if ver!="" else 1

    return runyear, runletter, ver

def create_name(parent, year, letter, ver):
    return f'{parent}_Run{year}{letter}_v{ver}'

xrd_redir = "root://xrootd-cms.infn.it//"
def main():
    with open("data_v2.txt", 'r') as f:
        datain = f.read()

    datasets = []
    for block in datain.split("\n\n"):
        if len(block)==0:
            continue
        lines = block.split("\n")

        das = lines[1]
        files = lines[3].split(" ")
        summary = eval(lines[5])[0]

        parent = get_parent(das)
        runyear, runletter, ver = get_runera(das)

        fnevents = [
            get_nevents(f'{xrd_redir}{fpath}')
            for fpath in files
        ]

        isdata = True
        name = create_name(parent, runyear, runletter, ver)
        print(name)
        nevents = summary["nevents"]
        sumweights = sum(fnevents)

        if nevents != sumweights:
            print(f'Mismatch summary {nevents} and file {sumweights} nevents')
        sumweights = float(sumweights)
        tree = "Events"
        xsec = None

        datasets.append({
            "name": name,
            "parent": parent,
            "isdata": isdata,
            "nevents": nevents,
            "sumweights": sumweights,
            "files": [f'{xrd_redir}{f}' for f in files],
            "file_nevents": fnevents,
            "DAS": das,
            "tree": tree,
            "xsection": xsec,
        })

    with open("data_v2.yaml", 'w') as f:
        yaml.dump(datasets, f, indent=4)


if __name__ == "__main__":
    main()
