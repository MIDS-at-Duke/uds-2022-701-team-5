import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from zipfile import ZipFile
from argparse import ArgumentParser

if __name__ == '__main__':
    arg_parse = ArgumentParser()
    arg_parse.add_argument("control_fips", help="fips county code for the control group", type=str)
    args = arg_parse.parse_args()

    DATA_PATH = "00_source_data"
    ARREST_DATA = os.path.join(DATA_PATH,
                               'ucr_arrests_monthly_all'
                               '_crimes_race_sex_1974_2020_dta.zip')
    with ZipFile(ARREST_DATA) as zip_file:
        dfs = {text_file.filename: pd.read_stata(zip_file.open(text_file.filename))
               for text_file in zip_file.infolist()
               if text_file.filename.endswith('.dta')}

    arrests_2019 = dfs['ucr_arrests_monthly_all_crimes_race_sex_2019.dta'].copy()
    arrests_2020 = dfs['ucr_arrests_monthly_all_crimes_race_sex_2020.dta'].copy()

    arrests_2019_cols = set(arrests_2019.columns)
    arrests_2020_cols = set(arrests_2020.columns)

    columns_to_remove = list(arrests_2020_cols.difference(arrests_2019_cols))
    arrests_2020.drop(columns_to_remove, axis=1, inplace=True)
    assert arrests_2019.shape[1] == arrests_2020.shape[1], "Columns number mismatch!"

    # Filter by state
    arrests_2020_filtered = arrests_2020.query("state_abb == 'CO'").copy()
    arrests_2019_filtered = arrests_2019.query("state_abb == 'CO'").copy()

    # Concatenate
    arrests_filtered = pd.concat([arrests_2020_filtered, arrests_2019_filtered], axis=0)
    arrests_filtered.loc[(arrests_filtered['fips_state_county_code'] == '') &
                         (arrests_filtered['agency_name'] == 'us secret service, denve'),
                         'fips_state_county_code'] = '08031'

    # Save ori and fips codes
    (arrests_filtered[['ori', 'fips_state_county_code']]
     .drop_duplicates()
     .to_csv("20_intermediate_files/ori.csv", index=False))

    # Filter by fips code
    fips_for_filter = args.control_fips.split("=")[1]
    arrests_filtered = (arrests_filtered
                        .query(f"fips_state_county_code in ['08031', '{fips_for_filter}']"))
    print(arrests_filtered.fips_state_county_code.unique())

    # Columns
    all_cols = arrests_2020_filtered.columns.to_list()
    general_cols = all_cols[:14]
    arrest_cols = [col for col in arrests_filtered.columns if 'tot_arrest' in col]
    violent_crime = ['agg_assault_tot_arrests', 'arson_tot_arrests',
                     'burglary_tot_arrests', 'manslaught_neg_tot_arrests',
                     'murder_tot_arrests', 'oth_assault_tot_arrests',
                     'oth_sex_off_tot_arrests', 'rape_tot_arrests',
                     'robbery_tot_arrests']
    non_violent = list(set(arrest_cols).difference(set(violent_crime)))

    arrests_filtered = arrests_filtered[general_cols + arrest_cols]

    # Aggregation
    group = ['month', 'year', 'fips_state_county_code']
    arrests_agg = (arrests_filtered
                   .groupby(group, as_index=False)[arrest_cols].sum())
    group1 = ['month', 'year', 'fips_state_county_code', 'fips_place_code']
    population_norm = (arrests_filtered
                       .groupby(group1, as_index=False)['population']
                       .max()
                       .groupby(group, as_index=False)[['population']]
                       .sum())
    merged = pd.merge(arrests_agg,
                      population_norm,
                      on=group)
    print(merged.shape)

    gen_cols = ['month', 'year', 'fips_state_county_code', 'population']
    non_violent_df = merged[gen_cols + non_violent].copy()

    # New columns
    non_violent_df['grand_total'] = np.sum(merged[non_violent], axis=1)
    non_violent_df['arrest_rate_gt'] = (non_violent_df['grand_total'] /
                                        non_violent_df['population'] * 100_000)

    non_violent_df['year'] = non_violent_df['year'].astype(str)
    non_violent_df['day'] = "01"
    non_violent_df['month'] = non_violent_df.month.str.capitalize()
    non_violent_df['date'] = pd.to_datetime(non_violent_df.year +
                                            "-" + non_violent_df.month +
                                            "-" + non_violent_df.day,
                                            format="%Y-%B-%d")
    post_treatment = "2020-June-01"
    treatment_group = "08031"

    condition1 = non_violent_df['date'] >= post_treatment
    non_violent_df['post_treatment'] = np.where(condition1, 1, 0)
    condition2 = non_violent_df['fips_state_county_code'] == treatment_group
    non_violent_df['treatment'] = np.where(condition2, 1, 0)

    model = smf.ols('arrest_rate_gt ~ treatment + post_treatment + treatment * post_treatment',
                    data=non_violent_df).fit()

    print(model.summary())
