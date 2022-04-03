from data_cleaning import  all_process
from pandas.api.types import CategoricalDtype
import seaborn as sns
import pandas as pd 

def plot_monthly_total_rate_trend(df: pd.DataFrame, col_type:str):
    """
    Input: a data frame contained monthly total crime rate 
    Input col_type : male, female, black, asian, amer_ind, white, hispanic, non_hispanic
    ouput: a graph that splits 2019 and 2020 by county
    """
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

def plot_monthly_certain_arrest_rate(df: pd.DataFrame, col_type: str, crime_type: str):
    """
    Input: a data frame contained monthly total crime rate 
    Input crime_type: a certain crime type for exampe: 'poss_drug_total', 
        'weapons', 'vandalism', 'prostitution' etc. 
    Input col_type : male, female, black, asian, amer_ind, white, hispanic, non_hispanic
    ouput: a graph that splits 2019 and 2020 by county
    """
    cat_type = CategoricalDtype(categories=[ 'january', 'february', 'march',
                                            'april', 'may', 'june', 'july','august', 'september',
                                            'october', 'november','december',], ordered=True)

    df['month'] = df['month'].astype(cat_type)
    # we only calculate the total arrest rate in the original function
    # now we're going to plot the rate so we need to calculate it here 
    sub_str = crime_type + '_tot_'+ col_type
    df[sub_str+'_rate'] = df[sub_str] / df['population'] * 100_000
    g = sns.FacetGrid(df, col="year", hue="fips_state_county_code")
    g.map(sns.lineplot, "month", sub_str+'_rate')
    g.set_xticklabels(rotation =45)
    g.fig.set_figwidth(10)
    g.fig.set_figheight(6)
    g.fig.suptitle(crime_type + ' of '+ col_type+' Trends by County')
    # change the legend to more descriptive county names 
    g.fig.legend(title='County_name',
                 labels=['Adams', 'Boulder','Broomfield','Denver','El Paso'],
                loc = 'upper right')




def main():
    DATA_PATH = "../00_source_data"
    arrests_data = os.path.join(
        DATA_PATH, "ucr_arrests_monthly_all" "_crimes_race_sex_1974_2020_dta.zip"
    )
    zip_file = ZipFile(arrests_data)
    dfs = {
        text_file.filename: pd.read_stata(zip_file.open(text_file.filename))
        for text_file in zip_file.infolist()
        if text_file.filename.endswith(".dta")
    }
    zip_file.close()
    arrests_2019 = dfs["ucr_arrests_monthly_all_crimes_race_sex_2019.dta"].copy()
    arrests_2020 = dfs["ucr_arrests_monthly_all_crimes_race_sex_2020.dta"].copy()
    # make sure we have the same set of the columns
    arrests_2019_cols = set(arrests_2019.columns)
    arrests_2020_cols = set(arrests_2020.columns)
    columns_to_remove = list(arrests_2020_cols.difference(arrests_2019_cols))
    arrests_2020.drop(columns_to_remove, axis=1, inplace=True)
    # filter by Colorado
    arrests_2020_filtered = arrests_2020.query("state_abb == 'CO'").copy()
    arrests_2019_filtered = arrests_2019.query("state_abb == 'CO'").copy()
    arrests_2020_filtered = arrests_2020.query(
        "fips_state_county_code in ['08031', '08013', '08014', '08001']"
    ).copy()
    arrests_2019_filtered = arrests_2019.query(
        "fips_state_county_code in ['08031', '08013', '08014', '08001']"
    ).copy()
    no_vio_b, vio_b = all_process('black', arrests_2020_filtered, arrests_2019_filtered)
    no_vio_a, vio_a = all_process('asian', arrests_2020_filtered, arrests_2019_filtered)
    no_vio_w, vio_w = all_process('white', arrests_2020_filtered, arrests_2019_filtered)
    no_vio_i, vio_i = all_process('amer_ind', arrests_2020_filtered, arrests_2019_filtered)
    plot_monthly_total_rate_trend(no_vio_b, 'black')
    plot_monthly_total_rate_trend(no_vio_a, 'asian')
    plot_monthly_total_rate_trend(no_vio_w, 'white')
    plot_monthly_total_rate_trend(no_vio_i, 'amer_ind')
    plot_monthly_certain_arrest_rate(no_vio_b, 'black', 'theft')




if __name__ == main:
    main()