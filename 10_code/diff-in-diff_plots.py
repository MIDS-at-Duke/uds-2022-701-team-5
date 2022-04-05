import pandas as pd
import numpy as np
import datetime as dt
import time
import warnings

warnings.filterwarnings("ignore")
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
import seaborn as sns
from linearmodels import PanelOLS

# Importing aggregates arrest data
df = pd.read_csv("./20_intermediate_files/aggregated.csv")

# converting date column from string to datetime
df["date"] = pd.to_datetime(df["date"])

# create new dataframes for pre and post STAR
pre_star = df[df["post_treatment"] == 0]
post_star = df[df["post_treatment"] == 1]

# split the dataframes further into treated and control groups
pre_star_treat = pre_star[pre_star["treatment"] == 1]
pre_star_control = pre_star[pre_star["treatment"] == 0]
post_star_treat = post_star[post_star["treatment"] == 0]
post_star_control = post_star[post_star["treatment"] == 0]

# calculate the average arrest rate for each county pre- and post-STAR

### Pre Treatment
pre_treat = pre_star_treat.groupby("date", as_index=False).mean()[
    ["arrest_rate_gt_arrests", "date"]
]
pre_control = pre_star_control.groupby("date", as_index=False).mean()[
    ["arrest_rate_gt_arrests", "date"]
]
### Post Treatment
post_treat = post_star_treat.groupby("date", as_index=False).mean()[
    ["arrest_rate_gt_arrests", "date"]
]
post_control = post_star_control.groupby("date", as_index=False).mean()[
    ["arrest_rate_gt_arrests", "date"]
]

# create arrays with x and y values for plotting

## Pre Treatment
x_pre_treat_arr = np.array(pre_treat[pre_treat["date"] < "2020-06-01"]["date"])
x_pre_treat_arr = mdates.date2num(x_pre_treat_arr)
y_pre_treat_arr = np.array(
    pre_treat[pre_treat["date"] < "2020-06-01"]["arrest_rate_gt_arrests"]
)
## Pre Control
x_pre_control_arr = np.array(pre_control[pre_control["date"] < "2020-06-01"]["date"])
x_pre_control_arr = mdates.date2num(x_pre_control_arr)
y_pre_control_arr = np.array(
    pre_control[pre_control["date"] < "2020-06-01"]["arrest_rate_gt_arrests"]
)
## Post Treatment
x_post_treat_arr = np.array(post_treat[post_treat["date"] >= "2020-06-01"]["date"])
x_post_treat_arr = mdates.date2num(x_post_treat_arr)
y_post_treat_arr = np.array(
    post_treat[post_treat["date"] >= "2020-06-01"]["arrest_rate_gt_arrests"]
)
## Post Control
x_post_control_arr = np.array(
    post_control[post_control["date"] >= "2020-06-01"]["date"]
)
x_post_control_arr = mdates.date2num(x_post_control_arr)
y_post_control_arr = np.array(
    post_control[post_control["date"] >= "2020-06-01"]["arrest_rate_gt_arrests"]
)


# plot the diff-in-diff
fig, ax = plt.subplots(figsize=(12, 8))

# Pre Control (BEFORE STAR - OTHER COUNTIES)
m, b = np.polyfit(x_pre_control_arr, y_pre_control_arr, 1)
plt.plot(mdates.num2date(x_pre_control_arr), m * x_pre_control_arr + b, color="blue")
ax = sns.regplot(x_pre_control_arr, y_pre_control_arr, ci=95, color="b", scatter=False)

# Post Control (AFTER STAR - OTHER COUNTIES)
m, b = np.polyfit(x_post_control_arr, y_post_control_arr, 1)
plt.plot(
    mdates.num2date(x_post_control_arr),
    m * x_post_control_arr + b,
    color="blue",
    label="Control",
)
sns.regplot(x_post_control_arr, y_post_control_arr, ci=95, color="b", scatter=False)

# Pre Treatment (BEFORE STAR - DENVER)
m, b = np.polyfit(x_pre_treat_arr, y_pre_treat_arr, 1)
plt.plot(mdates.num2date(x_pre_treat_arr), m * x_pre_treat_arr + b, color="red")
ax = sns.regplot(x_pre_treat_arr, y_pre_treat_arr, ci=95, color="r", scatter=False)

# Post Treatment (AFTER STAR - DENVER)
m, b = np.polyfit(x_post_treat_arr, y_post_treat_arr, 1)
plt.plot(
    mdates.num2date(x_post_treat_arr),
    m * x_post_treat_arr + b,
    color="red",
    label="Treatment",
)
sns.regplot(x_post_treat_arr, y_post_treat_arr, ci=95, color="r", scatter=False)

plt.xlabel("Month", fontsize=16)
plt.ylabel("Avg. Arrest Rate (per 100,000 people)", fontsize=16)
plt.title("Diff-in-Diff Analysis Arrests Rates Pre- and " "Post June 2020", fontsize=20)
plt.axvline(x=mdates.num2date(x_post_treat_arr[0]), color="black", ls=":")
plt.grid(b=True, which="major", color="#999999", linestyle="-", alpha=0.2)
plt.tick_params(labelsize=14)
plt.legend(loc="upper right", fontsize=16)
plt.show()
