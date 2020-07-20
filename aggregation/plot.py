from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def plot_aggregation_effects(
        fp: Path,
        x_col: str,
        y_col: str,
        color_col: str,
        **kwargs
):
    data = pd.read_csv(fp)

    factors, _ = data[color_col].factorize()
    data['color'] = factors

    fig = data.plot(
        kind='scatter',
        x=x_col,
        y=y_col,
        c='color',
        colormap='viridis',
        **kwargs
    )

    return fig


if __name__ == '__main__':
    data_dir = Path('../data/simulated')
    fig_dir = Path('../figures')

    files = data_dir.glob('aggregation_effects*.csv')

    for f in files:
        fig = plot_aggregation_effects(
            f,
            x_col='S_by_plot',
            y_col='S_by_page',
            color_col='level',
            title=f.stem[22:].capitalize(),
        )
        plt.savefig(fig_dir / f'{f.stem}.png')

    plt.show()
