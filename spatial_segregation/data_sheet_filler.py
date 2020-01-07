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
    Can be string, list of columns, 'all' or 'rest'.
    Default is None.
    """
    df = pd.read_excel(io=input_file, sheet_name=sheet)

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
    data_dir = '../data'
    os.chdir(data_dir)

    fill_data_sheet(
        'Viipurin henkikirjat.xlsx',
        'pop_by_plot_1880.xlsx',
        sheet='1880',
        columns='district plot_number',
        fill_with_zeros='rest',
    )
    fill_data_sheet(
        'Viipurin henkikirjat summat.xlsx',
        'pop_by_page_1880.xlsx',
        sheet='1880',
        columns='district plot_number',
        fill_with_zeros='rest',
    )
    fill_data_sheet(
        'Viipurin henkikirjat kaupunginosittain.xlsx',
        'pop_by_district_1880.xlsx',
        sheet='1880',
        columns='district',
        fill_with_zeros='rest',
    )
