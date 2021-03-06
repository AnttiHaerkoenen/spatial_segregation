import os

import pandas as pd

from old.src import data


def fill_data_sheet(
        input_file,
        output_file,
        sheet='Sheet1',
        columns='all',
        fill_with_zeros=None,
) -> None:
    """
    Fills gaps in excel data sheet using pandas.DataFrame.fillna().
    Fills columns given in columns-parameter using 'ffill'/'pad',
    and columns given in fill_with_zeros with a value of 0.
    :param input_file: Input filename
    :param output_file: Output filename
    :param sheet: name of the sheet
    :param columns: Names of columns to be filled.
    Can be string or list of columns or None or 'all'.
    Default is 'all'.
    :param fill_with_zeros: Names of columns to be filled with zeros.
    Can be string or list of columns or 'all'.
    Default is None.
    """
    df = pd.read_excel(io=input_file, sheetname=sheet)

    if not columns:
        columns = pd.Index([])
    elif columns == 'all':
        columns = df.columns
    elif isinstance(columns, str):
        columns = columns.split()
    else:
        columns = pd.Index(columns)

    if not fill_with_zeros:
        fill_with_zeros = pd.Index([])
    elif fill_with_zeros == 'all':
        fill_with_zeros = df.columns
    elif fill_with_zeros == 'rest':
        fill_with_zeros = pd.Index(set(df.columns) - set(columns))
    elif isinstance(columns, str):
        fill_with_zeros = fill_with_zeros.split()
    else:
        fill_with_zeros = pd.Index(fill_with_zeros)

    df[columns] = df[columns].fillna(method='pad', axis=0)
    df[fill_with_zeros] = df[fill_with_zeros].fillna(value=0)

    df.to_excel(output_file)


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    fill_data_sheet('example.xlsx', 'example2.xlsx', columns='district plot.number', fill_with_zeros='rest')
