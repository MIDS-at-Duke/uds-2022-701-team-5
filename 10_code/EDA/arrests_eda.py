from pandas.api.types import CategoricalDtype
import seaborn as sns
import pandas as pd
import numpy as np
import altair as alt


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


def plot_grouped_arrest_trend(df, arrest_type: str):
    """
    Plot mean arrest trend over time
    arrest_type: string specifying whether it's violent arrests or non-violent arrests
    """
    domain = ["Control", "Treatment"]
    range_ = ["blue", "red"]

    grouped_means = df.groupby(["treatment", "date"], as_index=False)[
        ["arrest_rate_gt_arrests"]
    ].mean()
    scatter = (
        alt.Chart(grouped_means)
        .mark_line()
        .encode(
            alt.X("date:T", scale=alt.Scale(zero=False), axis=alt.Axis(title="Date")),
            alt.Y(
                "arrest_rate_gt_arrests:Q",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(title="Arrest Rate (per 100,000 people)"),
            ),
            alt.Color(
                "treatment:N",
                legend=alt.Legend(title="Legend"),
                scale=alt.Scale(domain=domain, range=range_),
            ),
        )
    )
    rule = (
        alt.Chart(pd.DataFrame({"date": ["2020-06-01"], "color": ["black"]}))
        .mark_rule()
        .encode(x="date:T", color=alt.Color("color:N", scale=None))
    )

    return (scatter + rule).properties(
        title="Average Arrest Rate over Time (" + arrest_type + ")",
        width=600,
        height=350,
    )


def main():
    ## non violent arrests
    df_total_arrest = pd.read_csv("../20_intermediate_files/aggregated.csv")
    df_total_arrest["treatment"] = np.where(
        df_total_arrest["treatment"] == 1, "Treatment", "Control"
    )
    df_total_arrest_pre = df_total_arrest[df_total_arrest["post_treatment"] == 0]
    # df_total_arrest_post = df_total_arrest[df_total_arrest.loc["post_treatment"]==1]

    plot_monthly_total_rate_trend(df_total_arrest, "arrests")
    plot_monthly_total_rate_trend(df_total_arrest, "male")
    plot_monthly_total_rate_trend(df_total_arrest, "female")
    plot_monthly_total_rate_trend(df_total_arrest, "black")
    plot_monthly_total_rate_trend(df_total_arrest, "white")
    plot_monthly_total_rate_trend(df_total_arrest, "asian")
    plot_monthly_total_rate_trend(df_total_arrest, "amer_ind")
    plot_grouped_arrest_trend(df_total_arrest, "Non-violent")
    plot_grouped_arrest_trend(df_total_arrest_pre, "Non-violent")

    ## violent arrests
    df_total_arrest_vio = pd.read_csv(
        "../20_intermediate_files/aggregated_violent_arrest.csv"
    )
    df_total_arrest_vio["treatment"] = np.where(
        df_total_arrest_vio["treatment"] == 1, "Treatment", "Control"
    )
    df_total_arrest_vio_pre = df_total_arrest_vio[
        df_total_arrest_vio["post_treatment"] == 0
    ]
    # df_total_arrest__vio_post = df_total_arrest_vio[df_total_arrest_vio["post_treatment"]==1]

    plot_grouped_arrest_trend(df_total_arrest, "Both")
    plot_grouped_arrest_trend(df_total_arrest_vio, "Violent")
    plot_grouped_arrest_trend(df_total_arrest_vio_pre, "Violent")


if __name__ == main:
    main()
