import os
from pathlib import Path

import pandas as pd

from old.src import data


def fill_data_sheet(
        input_file: Path,
        output_file: Path,
        sheet='Sheet1',
        columns='all',
        output_format=None,
        fill_with_zeros=None,
) -> None:
    """
    Fills gaps in excel data sheet using pandas.DataFrame.fillna().
    Fills columns given in columns-parameter using 'ffill'/'pad',
    and columns given in fill_with_zeros with a value of 0.
    :param output_format: Which format to use for output. One of ('xlsx', 'csv').
    If None, format is inferred from file extension
    :param input_file: Input path
    :param output_file: Output path
    :param sheet: name of the sheet
    :param columns: Names of columns to be filled.
    Can be string or list of columns or None or 'all'.
    Default is 'all'.
    :param fill_with_zeros: Names of columns to be filled with zeros.
    Can be string, list of columns, 'all' or 'rest'.
    Default is None.
    """
    df = pd.read_excel(io=input_file, sheet_name=sheet)

    if not output_format:
        output_format = output_file.suffix.lstrip('.')

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

    df[fill_with_zeros] = df[fill_with_zeros].apply(pd.to_numeric)
    if output_format == 'xlsx':
        df.to_excel(output_file)
    elif output_format == 'csv':
        df.to_csv(output_file)


if __name__ == '__main__':
    data_dir = Path('../data')
    input_dir = data_dir / 'raw'
    output_dir = data_dir / 'intermediary'

    for year in range(1880, 1916, 5):
        fill_data_sheet(
            input_dir / 'Viipurin henkikirjat summat.xlsx',
            output_dir / f'pop_by_page_{year}.csv',
            sheet=f'{year}',
            columns='district page_number',
            fill_with_zeros='rest',
        )

    for year in 1880, :
        fill_data_sheet(
            input_dir / 'Viipurin henkikirjat.xlsx',
            output_dir / f'pop_by_plot_{year}.csv',
            sheet=f'{year}',
            columns='district plot_number',
            fill_with_zeros='rest',
        )

    for year in 1880, :
        fill_data_sheet(
            input_dir / 'Viipurin suostuntaveroluettelo.xlsx',
            output_dir / f'income_tax_record_{year}.csv',
            sheet=f'{year}',
            columns='district plot_number',
            fill_with_zeros='rest',
        )
