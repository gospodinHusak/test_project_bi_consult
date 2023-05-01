import pandas as pd


def cumsum_over(df: pd.DataFrame, partition_by: list, source_column:str) -> pd.DataFrame:
    return df.groupby(partition_by)[source_column].sum().groupby(level=0).cumsum().reset_index()


def convert_df_to_dash(df):
    ids = ["".join([col for col in multi_col if col]) for multi_col in list(df.columns)]
    cols = [{"name": list(col), "id": id_} for col, id_ in zip(list(df.columns), ids)]
    data = [{k: v for k, v in zip(ids, row)} for row in df.values]

    return cols, data
