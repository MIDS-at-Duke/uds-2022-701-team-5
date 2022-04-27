# %%
# importing required libraries
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import matplotlib as plt
import seaborn as sns
from datetime import datetime
import altair as alt

df_full = pd.read_csv("../20_intermediate_files/crime_rate.csv")

# %%
## Filtering data for pre treatment period
df_2020 = df_full.loc[
    (df_full["DATA_YEAR"] == 2020)
    & (df_full["month"].isin(["JAN", "FEB", "MAR", "APR", "MAY"]))
]
df_2019 = df_full.loc[df_full["DATA_YEAR"] == 2019]


# %%
# Checking if only pre treatment months are included
df_2020.month.value_counts()


# %%
# Combining 2019 and pre treatment 2020 df
df = pd.concat([df_2020, df_2019])


# %%
# Creating date and treatment columns for plots
df["date"] = pd.to_datetime(
    df.DATA_YEAR.astype(str) + "-" + df.month + "-01", format="%Y-%b-%d"
)
df["treatment"] = np.where(df["fips"] == 8031, 1, 0)
df_full["date"] = pd.to_datetime(
    df_full.DATA_YEAR.astype(str) + "-" + df_full.month + "-01", format="%Y-%b-%d"
)
df_full["treatment"] = np.where(df_full["fips"] == 8031, "Treatment", "Control")

# %%
# Seprating violent and non violent into 2 dataframes
df_violent = df.loc[df["violent_crime"] == 1, :]
df_nonviolent = df.loc[df["violent_crime"] == 0, :]
df_full_violent = df_full.loc[df_full["violent_crime"] == 1, :]
df_full_nonviolent = df_full.loc[df_full["violent_crime"] == 0, :]


# %%
# Function to create plots
def plot_crime_rate_trend(df, crime_type):
    domain = ["Control", "Treatment"]
    range_ = ["blue", "red"]
    grouped_means = df.groupby(["treatment", "date"], as_index=False)[
        ["crime_rate"]
    ].mean()
    scatter = (
        alt.Chart(grouped_means)
        .mark_line()
        .encode(
            alt.X("date:T", scale=alt.Scale(zero=False), axis=alt.Axis(title="Date")),
            alt.Y(
                "crime_rate:Q",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(title="Crime Rate (per 100,000 people)"),
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
        title="Average Crime Rate over Time (" + crime_type + ")", width=600, height=350
    )


# For Pre Treatment Period
plot_crime_rate_trend(df_nonviolent, "Non-Violent")
plot_crime_rate_trend(df_violent, "Violent")

# For complete review period
plot_crime_rate_trend(df_full_nonviolent, "Non-Violent")
plot_crime_rate_trend(df_full_violent, "Violent")
