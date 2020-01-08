import pandas as pd

__all__ = [
    "convert_table_to_fixed",
]

def convert_table_to_fixed(path, *tables):
    for table in tables:
        df = pd.read_hdf(path, table)
        df.reset_index(drop=True).to_hdf(
            path, table, format='fixed', append=False,
            complib='zlib', complevel=9,
        )
