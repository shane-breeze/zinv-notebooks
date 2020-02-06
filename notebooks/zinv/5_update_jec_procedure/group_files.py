import uproot
import oyaml as yaml
import pysge

max_events = 2_000_000

def get_event_count(path, tree="Events"):
    return uproot.open(path)[tree].numentries

def main():
    with open("paths_data.yaml", 'r') as f:
        paths = list(yaml.safe_load(f).keys())

    tasks = []
    for path in paths:
        tasks.append({
            "task": get_event_count,
            "args": (path,),
            "kwargs": {},
        })

    results = pysge.mp_submit(tasks, ncores=8)

    path_groups = [[]]
    event_count = 0
    for task, nevents in zip(tasks, results):
        event_count += nevents
        path_groups[-1].append(path)
        if event_count > max_events:
            path_groups.append([])
            event_count = 0

    with open("files_data.yaml", 'w') as f:
        yaml.dump(path_groups, f, indent=4)

if __name__ == "__main__":
    main()
