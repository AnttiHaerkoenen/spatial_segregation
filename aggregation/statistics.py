from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import stats

from spatial_segregation.data import aggregate_sum, prepare_pop_data


def get_plots_by_page(
        *,
        pop_by_plot: pd.DataFrame,
        pop_by_page: pd.DataFrame,
):
    districts = set(pop_by_page.district).intersection(set(pop_by_plot.district))

    plots_by_page = {}

    for district in districts:
        plot_data = pop_by_plot[pop_by_plot.district == district].drop(columns=['Unnamed: 0', 'district'])
        page_data = pop_by_page[pop_by_page.district == district].drop(columns=['Unnamed: 0', 'district'])

        plot_data = plot_data.set_index('plot_number').cumsum()
        page_data = page_data.set_index('page_number').cumsum()

        plot_iterator = plot_data.itertuples()
        page_iterator = page_data.itertuples()

        page_idx, *page = next(page_iterator)
        plots_in_district = {page_idx: []}

        for plot_idx, *plot in plot_iterator:

            if plot >= page:
                try:
                    page_idx, *page = next(page_iterator)
                    plots_in_district[page_idx] = [plot_idx]
                except StopIteration:
                    print(f'{district} empty, sums may not match')
                    plots_in_district[page_idx].append(plot_idx)

            else:
                plots_in_district[page_idx].append(plot_idx)
                print(f'{plot_idx} appended to {page_idx}')

        plots_by_page[district] = {k: set(v) for k, v in plots_in_district.items()}

    return plots_by_page


if __name__ == '__main__':
    data_dir = Path('../data/intermediary')
    num_cols = [
        'taxpayer_men', 'taxpayer_women', 'no_tax_men', 'no_tax_women',
        'in_russia_men', 'in_russia_women',
        'total_men', 'total_women', 'independent',
        'servants', 'unemployed', 'orthodox', 'other_christian',
        'other_religion', 'draftable',
    ]
    page_data = pd.read_csv(data_dir / 'pop_by_page_1880.csv')
    plot_data = pd.read_csv(data_dir / 'pop_by_plot_1880.csv')

    page_data[num_cols] = page_data[num_cols].astype('int32')
    plot_data[num_cols] = plot_data[num_cols].astype('int32')

    plots = get_plots_by_page(
        pop_by_plot=plot_data,
        pop_by_page=page_data,
    )

    plot_data_agg = aggregate_sum(
        plot_data,
        group_cols='district plot_number'.split(),
        target_cols=num_cols,
    )
    plot_data_agg = prepare_pop_data(plot_data_agg)
    print(plot_data_agg.columns)

    plot_data_agg.hist(
        column='lutheran',
        # by='district',
        bins=25,
    )

    plots = {
        k: [len(value) for value in v.values()]
        for k, v
        in plots.items()
    }
    plots = [(k, val) for k, v in plots.items() for val in v]
    plot_df = pd.DataFrame.from_records(plots, columns='district plots'.split())
    data = plot_df['plots']
    mu = float(data.mean())

    # plot_df.hist(by='district')

    # poisson_data = pd.Series(stats.distributions.poisson.rvs(mu, size=1000))
    # neg_binom_data = pd.Series(stats.distributions.nbinom.rvs(1, mu/28, size=1000))
    # beta_binom_data = pd.Series(stats.distributions.betabinom.rvs(28, 3, 12, size=1000))

    # beta_binom_data.plot(kind='kde')
    # fig = sm.qqplot_2samples(data, beta_binom_data, line='45')
    plt.show()
