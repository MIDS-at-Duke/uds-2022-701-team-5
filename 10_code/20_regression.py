import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

pd.set_option("display.max_columns", None)

DATA_PATH = "20_intermediate_files/aggregated.csv"
data = pd.read_csv(
    DATA_PATH, dtype={"fips_state_county_code": str}, parse_dates=["date"]
)
arrests_count_columns = data.columns.to_list()[5:12]
independent_vars = [
    "arrest_rate_gt_arrests",
    "arrest_rate_gt_black",
    "arrest_rate_gt_white",
    "arrest_rate_gt_asian",
    "arrest_rate_gt_amer_ind",
    "arrest_rate_gt_male",
    "arrest_rate_gt_female",
]
data["month"] = data.date.dt.month
data = (
    data.reset_index()
    .set_index(["fips_state_county_code", "month"])
    .drop("index", axis=1)
)

placebo = data.query("post_treatment == 0").copy()
fake_treatment = "2020-01-01"
placebo["post_treatment"] = np.where(placebo["date"] > fake_treatment, 1, 0)


def difference_in_difference(df):
    result = []

    for var in independent_vars:
        model = PanelOLS.from_formula(
            f"{var} ~ treatment + post_treatment"
            "+ treatment * post_treatment + EntityEffects + TimeEffects",
            df,
            drop_absorbed=True,
        ).fit(cov_type="clustered", cluster_entity=True)
        summary = model.summary
        summary_df = pd.DataFrame(summary.tables[1]).iloc[1:, :]
        summary_df.rename(
            {
                0: "coefficient name",
                1: "coef",
                2: "std err",
                3: "t",
                4: "p-value",
                5: "0.025",
                6: "0.975",
            },
            axis=1,
            inplace=True,
        )
        summary_df["independent variable"] = var
        result.append(summary_df)

    result_df = pd.concat(result, axis=0)
    return result_df


treatment = difference_in_difference(data)
placebo_test = difference_in_difference(placebo)

treatment.to_csv("20_intermediate_files/regression_results.csv", index=False)
placebo_test.to_csv("20_intermediate_files/placebo_test.csv", index=False)
