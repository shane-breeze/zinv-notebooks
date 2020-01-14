import pandas as pd
from . import geometry

__all__ = [
    "convert_table_to_fixed",
    "basic_query",
    "object_cross_cleaning",
]

def convert_table_to_fixed(path, *tables):
    """Simply read in a dataframe and output as a fixed table for quicker IO"""
    for table in tables:
        df = pd.read_hdf(path, table)
        df.reset_index(drop=True).to_hdf(
            path.replace(".h5", "_v2.h5"), table, format='fixed', append=False,
            complib='zlib', complevel=9,
        )

def basic_query(path, *cfgs):
    """Apply a query string to a dataframe and output into the same file"""
    for cfg in cfgs:
        df = pd.read_hdf(path, cfg["input"])
        df.query(cfg["query"]).reset_index().to_hdf(
            path, cfg["output"], format='fixed', append=False,
            complib='zlib', complevel=9,
        )

def object_cross_cleaning(path, *cfgs):
    """
    Remove objects from the input collection which match to any objects in any
    of the reference collections through a distance match in eta-phi space with
    a configurable cut.
    """
    for cfg in cfgs:
        # Retain the original dataframe for writing the skimmed version out
        df_orig = pd.read_hdf(path, cfg["input"])
        df = df_orig[[
            "parent_event", "object_id",
            cfg["columns"].format("eta"),
            cfg["columns"].format("phi"),
        ]].sort_values(["parent_event", "object_id"]).copy(deep=True)
        df.columns = ["parent_event", "object_id1", "eta1", "phi1"]
        df["matched"] = False

        for cfg_ref in cfg["references"]:
            df_ref = pd.read_hdf(path, cfg_ref["table"])[[
                "parent_event", "object_id",
                cfg_ref["columns"].format("eta"),
                cfg_ref["columns"].format("phi"),
            ]].sort_values(["parent_event", "object_id"])
            df_ref.columns = ["parent_event", "object_id2", "eta2", "phi2"]

            df_cross = df.merge(df_ref, on='parent_event', how='left')
            df_cross["matched"] = geometry.deltar(
                df_cross.eval("eta1-eta2").values,
                df_cross.eval("phi1-phi2").values,
            ) < cfg["distance"]

            # Default set to no match (False) and then take the logical OR with
            # any matched object of this particular reference
            df["matched"] = df["matched"] | (
                df_cross.groupby(["parent_event", "object_id1"])["matched"].any().values
            )

        df_orig.loc[df["matched"],:].reset_index(drop=True).to_hdf(
            path, cfg["output"], format='fixed', append=False,
            complib='zlib', complevel=9,
        )
