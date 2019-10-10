import glob
import pandas as pd
import pysge
import tables

def test_file(path):
    with pd.HDFStore(path, mode='r') as store:
        try:
            for branch in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
                for df in store.select("Events_jerSF{}".format(branch), iterator=True, chunksize=500_000):
                    print(df.shape)
        except tables.exceptions.HDF5ExtError:
            return False
    return True

paths = sorted(glob.glob("/vols/cms/sdb15/Analysis/ZinvWidth/databases/2019/08_Aug/28_Legacy/MC_jer/result_*.h5"))
tasks = [{
    "task": test_file,
    "args": (p,),
    "kwargs": {},
} for p in paths]

results = pysge.sge_submit(tasks, "test_file", "_ccsp_temp", options="-q hep.q -l h_vmem=24G -l h_rt=3:0:0")
for p, r in zip(paths, results):
    if not r:
        print(p)
