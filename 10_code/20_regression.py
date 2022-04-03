import pandas as pd
import statsmodels.formula.api as smf

pd.set_option("display.max_columns", None)

DATA_PATH = '20_intermediate_files/aggregated.csv'
data = pd.read_csv(DATA_PATH, dtype={'fips_state_county_code': str})
data = data.query("fips_state_county_code in ['08031', '08001', '08013']")
arrests_count_columns = data.columns.to_list()[5:12]
data_agg = (data
            .groupby(['date', 'treatment', 'post_treatment'],
                     as_index=False)[arrests_count_columns + ['population']]
            .sum())
data_agg['arrest_rate_gt_arrests'] = (data_agg['grand_total_arrests'] / data_agg['population'] * 100_000)
data_agg['arrest_rate_gt_black'] = (data_agg['grand_total_black'] / data_agg['population'] * 100_000)
data_agg['arrest_rate_gt_white'] = (data_agg['grand_total_white'] / data_agg['population'] * 100_000)
data_agg['arrest_rate_gt_asian'] = (data_agg['grand_total_asian'] / data_agg['population'] * 100_000)
data_agg['arrest_rate_gt_amer_ind'] = (data_agg['grand_total_amer_ind'] / data_agg['population'] * 100_000)
data_agg['arrest_rate_gt_male'] = (data_agg['grand_total_male'] / data_agg['population'] * 100_000)
data_agg['arrest_rate_gt_female'] = (data_agg['grand_total_female'] / data_agg['population'] * 100_000)

independent_vars = ['arrest_rate_gt_arrests', 'arrest_rate_gt_black',
                    'arrest_rate_gt_white', 'arrest_rate_gt_asian',
                    'arrest_rate_gt_amer_ind', 'arrest_rate_gt_male',
                    'arrest_rate_gt_female']

result = []

for var in independent_vars:
    model = smf.ols(f'{var} ~ treatment + post_treatment + treatment * post_treatment',
                    data_agg).fit()
    summary = model.summary()
    summary_df = pd.DataFrame(summary.tables[1]).iloc[1:, :]
    summary_df.rename({0: "coefficient name",
                       1: "coef",
                       2: "std err",
                       3: "t",
                       4: "p-value",
                       5: "0.025", 6: "0.975"}, axis=1, inplace=True)
    summary_df['independent variable'] = var
    result.append(summary_df)
result_df = pd.concat(result, axis=0)
result_df.to_csv("20_intermediate_files/regression_results.csv", index=False)
data_agg.to_csv("20_intermediate_files/data_for_regression.csv", index=False)
