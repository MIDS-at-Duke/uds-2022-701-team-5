from data_cleaning import all_process
from pandas.api.types import CategoricalDtype
import seaborn as sns
import pandas as pd


def plot_monthly_total_rate_trend(df: pd.DataFrame, col_type: str):
    """
    Input: a data frame contained monthly total crime rate
    Input col_type : male, female, black, asian, amer_ind, white, arrests
    ouput: a graph that splits 2019 and 2020 by county
    """
    # convert month from string to categorial in order to sort them
    cat_type = CategoricalDtype(
        categories=[
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        ordered=True,
    )

    df["month"] = df["month"].astype(cat_type)
    g = sns.FacetGrid(df, col="year", hue="fips_state_county_code")
    sub_str = "arrest_rate_gt_" + col_type
    g.map(sns.lineplot, "month", sub_str)
    g.set_xticklabels(rotation=45)
    g.fig.set_figwidth(10)
    g.fig.set_figheight(6)
    g.fig.suptitle("Total Crime Rate Trends of " + col_type + " by County")
    g.fig.legend(
        title="County_name",
        labels=["Adams", "Boulder", "Broomfield", "Denver", "El Paso"],
        loc="upper right",
    )


def plot_monthly_certain_arrest_rate(df: pd.DataFrame, col_type: str, crime_type: str):
    """
    Input: a data frame contained monthly total crime rate
    Input crime_type: a certain crime type for exampe: 'poss_drug_total',
        'weapons', 'vandalism', 'prostitution' etc.
    Input col_type : male, female, black, asian, amer_ind, white, hispanic, non_hispanic
    ouput: a graph that splits 2019 and 2020 by county
    """
    cat_type = CategoricalDtype(
        categories=[
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ],
        ordered=True,
    )

    df["month"] = df["month"].astype(cat_type)
    # we only calculate the total arrest rate in the original function
    # now we're going to plot the rate so we need to calculate it here
    sub_str = crime_type + "_tot_" + col_type
    df[sub_str + "_rate"] = df[sub_str] / df["population"] * 100_000
    g = sns.FacetGrid(df, col="year", hue="fips_state_county_code")
    g.map(sns.lineplot, "month", sub_str + "_rate")
    g.set_xticklabels(rotation=45)
    g.fig.set_figwidth(10)
    g.fig.set_figheight(6)
    g.fig.suptitle(crime_type + " of " + col_type + " Trends by County")
    # change the legend to more descriptive county names
    g.fig.legend(
        title="County_name",
        labels=["Adams", "Boulder", "Broomfield", "Denver", "El Paso"],
        loc="upper right",
    )


def main():
    df_total_arrest = pd.read_csv("./20_intermediate_files/aggregated.csv")
    plot_monthly_total_rate_trend(df_total_arrest, "arrests")
    plot_monthly_total_rate_trend(df_total_arrest, "male")
    plot_monthly_total_rate_trend(df_total_arrest, "female")
    plot_monthly_total_rate_trend(df_total_arrest, "black")
    plot_monthly_total_rate_trend(df_total_arrest, "white")
    plot_monthly_total_rate_trend(df_total_arrest, "asian")
    plot_monthly_total_rate_trend(df_total_arrest, "amer_ind")


if __name__ == main:
    main()
