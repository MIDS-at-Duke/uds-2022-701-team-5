import os
import numpy as np
import pandas as pd

from zipfile import ZipFile


def load_data():
    """

    :return:
    """
    with ZipFile(ARREST_DATA) as zip_file:
        dfs = {text_file.filename: pd.read_stata(zip_file.open(text_file.filename))
               for text_file in zip_file.infolist()
               if text_file.filename.endswith('.dta')}

    a_2019 = dfs['ucr_arrests_monthly_all_crimes_race_sex_2019.dta'].copy()
    a_2020 = dfs['ucr_arrests_monthly_all_crimes_race_sex_2020.dta'].copy()

    return a_2019, a_2020


def match_columns(df1, df2):
    """

    :param df1:
    :param df2:
    :return:
    """
    df1_cols = set(df1.columns)
    df2_cols = set(df2.columns)

    if len(df1_cols) > len(df2_cols):
        cols_remove = list(df1_cols.difference(df2_cols))
        return df1.drop(cols_remove, axis=1), df2
    elif len(df1_cols) < len(df2_cols):
        cols_remove = list(df2_cols.difference(df1_cols))
        return df1, df2.drop(cols_remove, axis=1)
    elif df1_cols == df2_cols:
        return df1, df2
    else:
        raise ValueError("Take a look!")


def filter_by_state_concat(df1, df2, state='CO'):
    """

    :return:
    """
    df1 = df1.query(f"state_abb == '{state}'")
    df2 = df2.query(f"state_abb == '{state}'")
    return pd.concat([df1, df2], axis=0)


def filter_columns(col_type: str, df):
    """

    :return:
    """
    violent_crime_c = ['agg_assault_tot', 'arson_tot', 'burglary_tot',
                       'manslaught_neg_tot', 'murder_tot', 'oth_assault_tot',
                       'oth_sex_off_tot', 'rape_tot', 'robbery_tot']
    cols = [col for col in df.columns if col.endswith('tot_' + col_type)]
    violent_s = [i + '_' + col_type for i in violent_crime_c]
    non_violent_columns = list(set(cols).difference(set(violent_s)))
    return non_violent_columns


def data_with_relevant_columns(df):
    all_cols = df.columns.to_list()
    general_cols = all_cols[:14]
    categories = ['arrests', 'black', 'white', 'asian', 'male', 'female']
    relevant_cols = general_cols
    for cat in categories:
        col = filter_columns(cat, df)
        relevant_cols += col
    return df[relevant_cols]


def population(df, group1, group2, save=False):
    """

    :param save:
    :param df:
    :param group1:
    :param group2:
    :return:
    """
    population_data = (df
                       .groupby(group1, as_index=False)['population']
                       .max()
                       .groupby(group2, as_index=False)[['population']]
                       .sum())
    if save:
        population_data.to_csv("20_intermediate_files/population.csv", index=False)
    return population_data


def create_new_columns(df):
    """

    :param df:
    :return:
    """
    # Lists of non-violent crimes per demographic group:
    non_violent_arrests = filter_columns("arrests", df)
    non_violent_black = filter_columns("black", df)
    non_violent_white = filter_columns("white", df)
    non_violent_asian = filter_columns("asian", df)
    non_violent_male = filter_columns("male", df)
    non_violent_female = filter_columns("female", df)

    # Add date column for easier filtering by date
    df['year'] = df['year'].astype(str)
    df['day'] = "01"
    df['month'] = df.month.str.capitalize()
    df['date'] = pd.to_datetime(df.year + "-" + df.month +
                                "-" + df.day, format="%Y-%B-%d")
    df.drop("day", axis=1, inplace=True)

    # Sum over all non violent crimes:
    df['grand_total_arrests'] = np.sum(merged[non_violent_arrests], axis=1)
    df['grand_total_black'] = np.sum(merged[non_violent_black], axis=1)
    df['grand_total_white'] = np.sum(merged[non_violent_white], axis=1)
    df['grand_total_asian'] = np.sum(merged[non_violent_asian], axis=1)
    df['grand_total_male'] = np.sum(merged[non_violent_male], axis=1)
    df['grand_total_female'] = np.sum(merged[non_violent_female], axis=1)

    # Crime rate:
    df['arrest_rate_gt_arrests'] = (df['grand_total_arrests'] / df['population'] * 100_000)
    df['arrest_rate_gt_black'] = (df['grand_total_black'] / df['population'] * 100_000)
    df['arrest_rate_gt_white'] = (df['grand_total_white'] / df['population'] * 100_000)
    df['arrest_rate_gt_asian'] = (df['grand_total_asian'] / df['population'] * 100_000)
    df['arrest_rate_gt_male'] = (df['grand_total_male'] / df['population'] * 100_000)
    df['arrest_rate_gt_female'] = (df['grand_total_female'] / df['population'] * 100_000)

    # Drop redundant columns:
    df.drop(non_violent_arrests + non_violent_black + non_violent_asian +
            non_violent_male + non_violent_female + non_violent_white,
            axis=1, inplace=True)

    # Add post treatment and treatment columns:
    post_treatment = "2020-June-01"
    treatment_group = "08031"
    condition1 = df['date'] >= post_treatment
    condition2 = df['fips_state_county_code'] == treatment_group
    df['post_treatment'] = np.where(condition1, 1, 0)
    df['treatment'] = np.where(condition2, 1, 0)
    return df


if __name__ == '__main__':
    DATA_PATH = "00_source_data"
    ARREST_DATA = os.path.join(DATA_PATH,
                               'ucr_arrests_monthly_all'
                               '_crimes_race_sex_1974_2020_dta.zip')
    arrests_2019, arrests_2020 = load_data()
    arrests_2019, arrests_2020 = match_columns(arrests_2019, arrests_2020)
    arrest_concat = filter_by_state_concat(arrests_2019, arrests_2020)

    # Impute fips code based on agency name
    arrest_concat.loc[(arrest_concat['fips_state_county_code'] == '') &
                      (arrest_concat['agency_name'] == 'us secret service, denve'),
                      'fips_state_county_code'] = '08031'

    # Save ori and fips codes
    # (arrest_concat[['ori', 'fips_state_county_code']]
    #  .drop_duplicates()
    #  .to_csv("20_intermediate_files/ori.csv", index=False))

    # Filter by fips code
    fips_codes = ['08031', '08013', '08014', '08001', '08041']
    arrest_concat = arrest_concat.query(f"fips_state_county_code in {fips_codes}")

    # Filter columns
    arrest_concat = data_with_relevant_columns(arrest_concat)

    # Aggregation
    group1 = ['month', 'year', 'fips_state_county_code', 'fips_place_code']
    group2 = ['month', 'year', 'fips_state_county_code']
    population_norm = population(arrest_concat, group1, group2)
    cols_to_aggregate = arrest_concat.columns.to_list()[14:]

    arrests_agg = (arrest_concat
                   .groupby(group2, as_index=False)[cols_to_aggregate]
                   .sum())

    merged = pd.merge(arrests_agg,
                      population_norm,
                      on=group2)

    final_df = create_new_columns(merged)
    final_df.to_csv("20_intermediate_files/aggregated.csv", index=False)
