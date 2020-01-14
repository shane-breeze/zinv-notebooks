import argparse
import glob
import oyaml as yaml
import numpy as np
import importlib
import pysge

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("cfg", type=str, help="Config file to use")
    parser.add_argument("modules", type=str, help="Modules to run")
    parser.add_argument("paths", type=str, help="Paths to run over")
    parser.add_argument(
        "--njobs", "-n", type=int, default=-1,
        help="Number of jobs to create",
    )
    parser.add_argument(
        "--pysge_func", type=str, default="local_submit",
        help="pysge submission function",
    )
    parser.add_argument(
        "--pysge_args", type=str, default="",
        help="pysge submission arguments. Comma-delimited.",
    )
    parser.add_argument(
        "--pysge_kwargs", type=str, default="",
        help="pysge submission kwargs. Comma-delimited, equals-separated.",
    )
    parser.add_argument(
        "--verbose", "-v", default=False, action="store_true",
        help="Verbose print out whilst running",
    )
    parser.add_argument(
        "--print-modules", default=False, action="store_true",
        help="Print available modules",
    )
    return parser.parse_args()

def open_config(path):
    with open(path, 'r') as f:
        cfg = yaml.full_load(f)
    return cfg

def get_list_of_files(paths, njobs=-1):
    full_paths = []
    for p in paths.split(","):
        full_paths.extend(list(glob.glob(p)))
    if njobs > 0:
        full_paths = np.array_split(full_paths, args.njobs)
    else:
        full_paths = [[p] for p in full_paths]
    return full_paths

def create_tasks(cfg, modules, paths, verbose=False):
    def task(_cfg, _modules, _paths, _verbose=False):
        results = []
        for _path in _paths:
            if _verbose:
                print(_path)
            for _module in _modules:
                if _verbose:
                    print(_module)
                _tcfg = _cfg[_module]
                imported_module_name, func_name = _tcfg["func"].split(":")
                imported_module = importlib.import_module(imported_module_name)
                func = getattr(imported_module, func_name)
                results.append(func(
                    _path, *_tcfg.get("args", []), **_tcfg.get("kwargs", {}),
                ))
        return results

    return [{
        "task": task,
        "args": (cfg, modules, subpaths),
        "kwargs": {"_verbose": verbose},
    } for subpaths in paths]

def main():
    options = parse_args()

    cfg = open_config(options.cfg)
    if options.print_modules:
        print(cfg.keys())
        return

    paths = get_list_of_files(options.paths, options.njobs)
    tasks = create_tasks(
        cfg, options.modules.split(","), paths, verbose=options.verbose,
    )

    args = [tasks]+list(options.pysge_args.split(","))
    kwargs = {}
    if len(options.pysge_kwargs)>0:
        kwargs = dict([
            k.split("=")
            for k in options.pysge_kwargs.split(",")
        ])
    results = getattr(pysge, options.pysge_func)(*args, **kwargs)

if __name__ == "__main__":
    main()
