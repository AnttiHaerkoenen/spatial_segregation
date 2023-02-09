import os
from pathlib import Path
from typing import Sequence

import pandas as pd

import data


def fill_data_sheet(
        input_file: Path,
        output_file: Path,
        index_columns: Sequence[str],
        fill_with_zeros=None,
        sheet='Sheet1',
        output_format=None,
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
    :param index_columns: Names of columns to be filled. Must be a sequence of columns
    :param fill_with_zeros: Names of columns to be filled with zeros.
    Can be string, list of columns, 'all' or 'rest'.
    Default is None.
    """
    df = pd.read_excel(
        io=input_file,
        sheet_name=sheet,
        dtype={col: str for col in index_columns},
    )
    print(f'Wrote sheet {sheet} from {input_file}')

    if not output_format:
        output_format = output_file.suffix.lstrip('.')

    if not fill_with_zeros:
        fill_with_zeros = pd.Index([])
    elif fill_with_zeros == 'all':
        fill_with_zeros = df.columns
    elif fill_with_zeros == 'rest':
        fill_with_zeros = pd.Index(set(df.columns) - set(index_columns))
    elif isinstance(index_columns, str):
        fill_with_zeros = fill_with_zeros.split()
    else:
        fill_with_zeros = pd.Index(fill_with_zeros)

    df[index_columns] = df[index_columns].fillna(method='pad', axis=0).applymap(str)
    df[fill_with_zeros] = df[fill_with_zeros].fillna(value=0).applymap(pd.to_numeric)

    if output_format == 'xlsx':
        df.to_excel(output_file)
    elif output_format == 'csv':
        df.to_csv(output_file)


if __name__ == '__main__':
    data_dir = Path('./data')
    input_dir = data_dir / 'raw'
    output_dir = data_dir / 'interim'

    YEARS = list(range(1880, 1921, 5)) + [1883, 1888, 1902, 1913]

    if not output_dir.exists():
        output_dir.mkdir()

    for year in YEARS:
        fill_data_sheet(
            input_dir / 'Viipurin henkikirjat summat.xlsx',
            output_dir / f'pop_by_page_{year}.csv',
            sheet=f'{year}',
            index_columns='district page_number representative_plot'.split(),
            fill_with_zeros='rest',
        )

    for year in (1880, 1900, 1915):
        fill_data_sheet(
            input_dir / 'Viipurin henkikirjat.xlsx',
            output_dir / f'pop_by_plot_{year}.csv',
            sheet=f'{year}',
            index_columns='district plot_number'.split(),
            fill_with_zeros='rest',
        )

    for year in 1880, :
        fill_data_sheet(
            input_dir / 'Viipurin suostuntaveroluettelo.xlsx',
            output_dir / f'income_tax_record_{year}.csv',
            sheet=f'{year}',
            index_columns='district plot_number'.split(),
            fill_with_zeros='rest',
        )
