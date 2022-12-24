"""Module for loading & saving parquet files"""

import os

import pyarrow
from pyarrow import parquet, BufferReader
import awswrangler as wr
import pandas as pd

from pynba import constants


def load_pq_to_df(source, *args, **kwargs):
    """
    Load Parquet into Pandas, either using:
        1) awswrangler.s3.read_parquet if the source starts with "s3"
        https://aws-data-wrangler.readthedocs.io/en/2.4.0-docs/stubs/awswrangler.s3.read_parquet.html

        or
        2) pyarrow.parquet.read_table
        https://arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table.html

    Parameters
    ----------
    source : str, pyarrow.NativeFile, or file-like object

    Returns
    -------
    pd.DataFrame
    """
    try:
        is_s3 = source.startswith(constants.S3)
    except AttributeError:
        is_s3 = False  # file-like objects aren't s3
        source = BufferReader(source.read())
    if is_s3:
        return _convert_dtypes(wr.s3.read_parquet(source, *args, **kwargs))
    return parquet.read_table(source, *args, **kwargs).to_pandas()


def save_df_to_pq(dataframe, where, *args, **kwargs):
    """
    Save Pandas to Parquet, either using:
    1) pyarrow.parquet.write_table is where file extension is ".parquet"
    https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html

    or
    2) pyarrow.parquet.write_dataset
    https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_to_dataset.html

    Parameters
    ----------
    dataframe : pd.DataFrame
    where : string, pathlib.Path, or pyarrow.NativeFile
    """
    table = pyarrow.Table.from_pandas(dataframe, preserve_index=False)
    try:
        is_single_file = os.path.splitext(where)[-1] == ".parquet"
    except AttributeError:
        is_single_file = True  # file-like objects are single files
    if is_single_file:
        parquet.write_table(table, where, *args, **kwargs)
    else:
        parquet.write_to_dataset(table, where, *args, **kwargs)


def _convert_dtypes(dataframe):
    """
    Pandas new extension dtypes are not ready for
    primetime, so let's clean convert them away.
    """
    for name, dtype in dataframe.dtypes.items():
        if pd.api.types.is_extension_array_dtype(dtype):
            new_dtype = type(dataframe[name].iloc[0])
            dataframe[name] = dataframe[name].astype(new_dtype, copy=False)
    return dataframe
