from pathlib import Path

import pandas as pd


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
            print(plot, page)

            if plot >= page:

                try:
                    page_idx, *page = next(page_iterator)
                    plots_in_district[page_idx] = [plot_idx]
                except StopIteration:
                    raise ValueError(f'{district} empty, sums may not match')

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

    print(plots)
