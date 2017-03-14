import os

import pandas as pd
import numpy as np

from src import data


def fill_data_sheet(filename, sheet='Sheet1', columns='all'):
    df = pd.read_excel(io=filename, sheetname=sheet)
    if columns == 'all':
        columns = df.columns
    elif isinstance(columns, str):
        columns = columns.split()
    else:
        columns = pd.Index(columns)
        print(columns)

    df[columns] = df[columns].fillna(method='ffill', axis=0)

    df.to_excel(filename)


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    fill_data_sheet('example.xlsx')
