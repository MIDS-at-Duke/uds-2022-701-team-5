
import os
import numpy as np
import pandas as pd
from zipfile import ZipFile
import seaborn as sns
from pandas.api.types import CategoricalDtype


def filter_columns(col_type: str, df): 
    """
    Input column type : male, female, black, asian, amer_ind, white, hispanic, non_hispanic
    Input DF: 2019 dataframe or 2020 dataframe (filtered by Colorado and county code already)
    Return: Data frame with columns we want 
    """
    general_cols = df.columns.to_list()[:14]
    cols = [col for col in df.columns if col.endswith('tot_'+ col_type)]
    filtered = df[general_cols + cols]
    return filtered, cols




def merge_data(df_2019, df_2020, cols):
    # concat two data frame to one 
    arrests_df = pd.concat([df_2019, df_2020], axis=0)
    arrests_agg = (arrests_df
               .groupby(['month', 'year', 'fips_state_county_code'], as_index=False)[cols].sum())
    population_norm = (arrests_df
                   .groupby(['month', 'year', 'fips_state_county_code', 'fips_place_code'], as_index=False)[
                       'population']
                   .max()
                   .groupby(['month', 'year', 'fips_state_county_code'], as_index=False)[['population']]
                   .sum())
    merged = pd.merge(arrests_agg, population_norm, on=['month', 'year', 'fips_state_county_code'])
    return merged



def violent_crime_split(merged_data, col_type: str ):
    """
    Input: merged data that contains dataframe from 2019 and 2020
    Input column type : male, female, black, asian, amer_ind, white, hispanic, non_hispanic
    ouput: dataframe with non violent, and a dataframe with violent
    """
    violent_crime = ['agg_assault_tot', 'arson_tot', 'burglary_tot',
                 'manslaught_neg_tot', 'murder_tot', 'oth_assault_tot',
                 'oth_sex_off_tot', 'rape_tot', 'robbery_tot']
    violent_s = [i+'_'+col_type for i in violent_crime]
    gen_col = ['month', 'year', 'fips_state_county_code', 'population']
    non_violent_s = list(set(merged_data.columns).difference(set(violent_s+gen_col )))
    non_violent_df = merged_data[['month', 'year', 'fips_state_county_code', 'population'] + non_violent_s].copy()
    violent_df = merged_data[['month', 'year', 'fips_state_county_code', 'population'] + violent_s].copy()
    violent_df['grand_total_'+col_type] = np.sum(violent_df[violent_s], axis=1)
    non_violent_df['grand_total_'+col_type] = np.sum(non_violent_df[non_violent_s], axis=1)
    non_violent_df['rate_gt_'+col_type] = non_violent_df['grand_total_'+col_type] / non_violent_df['population'] * 100_000
    violent_df['rate_gt_'+col_type] = violent_df['grand_total_'+col_type] / violent_df['population'] * 100_000
    return non_violent_df, violent_df 

def main():
    # read from the zip file
    DATA_PATH = "../00_source_data"
    arrests_data = os.path.join(DATA_PATH, 'ucr_arrests_monthly_all'
                                        '_crimes_race_sex_1974_2020_dta.zip')
    zip_file = ZipFile(arrests_data)
    dfs = {text_file.filename: pd.read_stata(zip_file.open(text_file.filename))
        for text_file in zip_file.infolist()
        if text_file.filename.endswith('.dta')}
    zip_file.close()
    arrests_2019 = dfs['ucr_arrests_monthly_all_crimes_race_sex_2019.dta'].copy()
    arrests_2020 = dfs['ucr_arrests_monthly_all_crimes_race_sex_2020.dta'].copy()
    # make sure we have the same set of the columns 
    arrests_2019_cols = set(arrests_2019.columns)
    arrests_2020_cols = set(arrests_2020.columns)
    columns_to_remove = list(arrests_2020_cols.difference(arrests_2019_cols))
    arrests_2020.drop(columns_to_remove, axis=1, inplace=True)
    # filter by Colorado
    arrests_2020_filtered = arrests_2020.query("state_abb == 'CO'").copy()
    arrests_2019_filtered = arrests_2019.query("state_abb == 'CO'").copy()
    arrests_2020_filtered = arrests_2020.query("fips_state_county_code in ['08031', '08013', '08014', '08001']").copy()
    arrests_2019_filtered = arrests_2019.query("fips_state_county_code in ['08031', '08013', '08014', '08001']").copy()
    # the following are split using male data, we can run different sub columns
    filtered_2020 = filter_columns('arrest',arrests_2020_filtered)[0]
    filtered_2019 = filter_columns('arrest',arrests_2019_filtered)[0]
    column_list = filter_columns('arrest',arrests_2019_filtered)[1]
    merged_df = merge_data(filtered_2020, filtered_2019, column_list)
    no_vio, vio = violent_crime_split(merged_df, 'arrests')

    # plots 
    cat_type = CategoricalDtype(categories=[ 'january', 'february', 'march',
    'april', 'may', 'june', 'july','august', 'september', 'october', 'november',
    'december',], ordered=True)

    no_vio['month'] = no_vio['month'].astype(cat_type)
    g = sns.FacetGrid(no_vio, col="year", hue="fips_state_county_code")
    g.map(sns.lineplot, "month", "rate_gt_arrests")
    g.set_xticklabels(rotation =45)
    g.fig.set_figwidth(10)
    g.fig.set_figheight(6)
    g.fig.suptitle('Non-violent Crime Trends by County ')
    g.add_legend()