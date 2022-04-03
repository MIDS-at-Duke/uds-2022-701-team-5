from data_cleaning import 
from pandas.api.types import CategoricalDtype
import seaborn as sns


def plot_monthly_rate_trend(df, col_type:str):
    # convert month from string to categorial in order to sort them 
    cat_type = CategoricalDtype(categories=[ 'january', 'february', 'march','april'
                                            , 'may', 'june', 'july','august', 'september',
                                            'october', 'november', 'december',], ordered=True)

    df['month'] = df['month'].astype(cat_type)
    # plot a side by side graph by different year
    g = sns.FacetGrid(df, col="year", hue="fips_state_county_code")
    sub_str = "rate_gt_"+col_type
    g.map(sns.lineplot, "month", sub_str)
    g.set_xticklabels(rotation =45)
    g.fig.set_figwidth(10)
    g.fig.set_figheight(6)
    g.fig.suptitle('Total Crime Rate Trends of ' + col_type + ' by County')
    # change the legend to more descriptive county names 
    g.fig.legend(title='County_name',
                 labels=['Adams', 'Boulder','Broomfield','Denver','El Paso'],
                loc = 'upper right')


def main():
    plot_monthly_rate_trend(data_m, 'male')




if __name__ == main:
    main()