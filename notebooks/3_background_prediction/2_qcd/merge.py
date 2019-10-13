import zdb
import glob
import os
import pysge

path = "/vols/build/cms/sdb15/ZinvWidth/zinv-notebooks/notebooks/background_prediction/qcd/_ccsp_temp/tpd_20190921_235846_7gfcmkx_/task_*/result.p.lz4"
paths = sorted([p for p in glob.glob(path)])

def job(_paths, _outpath):
    df = zdb.modules.df_process.df_open_merge(paths)
    outfile, outtable = _outpath.split(":")
    df.to_hdf(
        outfile, outtable, format='table',
        append=True, complevel=9, complib='zlib',
    )

outpaths = [
    "data/hists_qcd_estimation.h5:DataAggEvents",
    "data/hists_qcd_estimation.h5:MCAggEvents",
    "data/hists_qcd_estimation.h5:MCAggEvents_jes",
    "data/hists_qcd_estimation.h5:MCAggEvents_jer",
    "data/hists_qcd_estimation.h5:MCAggEvents_unclust",
    "data/hists_qcd_estimation.h5:MCAggEvents_lepscales",
]

tasks = []
for idx, outpath in enumerate(outpaths):
    start = 10*idx
    stop = min(10*(idx+1), len(paths))

    tasks.append({
        "task": job,
        "args": (
            [os.path.abspath(p) for p in paths[start:stop]],
            os.path.abspath(outpath),
        ),
        "kwargs": {},
    })

pysge.sge_submit(
    tasks, "merge", "_ccsp_temp",
    options="-q hep.q -l h_vmem=24G -pe hep.pe 8",
)
