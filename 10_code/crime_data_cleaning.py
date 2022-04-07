# %% [markdown]
# ## Crime Data Cleaning

# %%
import pandas as pd
import numpy as np

# %%
# load source data
agencies = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/00_source_data/agencies.csv")
offense_type = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/00_source_data/NIBRS_offense_type.csv")
incident_19 = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/00_source_data/2019_NIBRS_incident.csv")
incident_20 = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/00_source_data/2020_NIBRS_incident.csv")
offense_19 = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/00_source_data/2019_NIBRS_offense.csv")
offense_20 = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/00_source_data/2020_NIBRS_offense.csv")

# %%
# load intermediate data with fips codes, ori numbers and population
fips = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/20_intermediate_files/ori.csv")
pop = pd.read_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/20_intermediate_files/population.csv")

# %%
# combine 2019 and 2020 data
all_incidents = pd.concat([incident_19, incident_20])
all_offenses = pd.concat([offense_19, offense_20])

# %%
# subset to just the columns we want
agencies = agencies[["COUNTY_NAME","AGENCY_ID","ORI"]]

# %%
# change ori to be a string
fips["ORI"] = fips["ori"].astype(str)

# %%
# add trailing zeros to the ORI number
fips['ORI'] = fips['ORI'].apply(lambda x: x.ljust(2 + len(x), '0'))

# %%
# make sure it worked
fips.ORI.head()

# %%
# merge agencies and fips on ORI number
merged_ori = pd.merge(fips, agencies, on="ORI", how="inner")

# %%
# remove nan values
merged_ori = merged_ori.loc[merged_ori["fips_state_county_code"].isna() == False].copy()

# %%
# change fips code to string value
merged_ori["fips"] = merged_ori.fips_state_county_code.astype(str).str[:4]
pop['fips'] = pop.fips_state_county_code.astype(str)

# %%
# add a leading zero to the fips code
merged_ori['fips'] = merged_ori['fips'].apply(lambda x: x.zfill(5))
pop['fips'] = pop['fips'].apply(lambda x: x.zfill(5))

# %%
# check to make sure it worked
merged_ori.fips.unique()

# %%
pop.fips.unique()

# %%
# merge all offenses to general offense table to get offense category name
merged_offenses = pd.merge(all_offenses,offense_type[['OFFENSE_TYPE_ID','OFFENSE_CATEGORY_NAME']],on='OFFENSE_TYPE_ID', how='left', validate='m:m', indicator=True)

# %%
# check to make sure it worked
merged_offenses._merge.value_counts()

# %%
# merge all incidents to the fips code
merged_incidents = pd.merge(all_incidents,merged_ori[['AGENCY_ID','COUNTY_NAME','fips']],on='AGENCY_ID', how='left', validate='m:1', indicator=True)

# %%
# check how many agencies do not have a fips code
merged_incidents._merge.value_counts()

# %%
merged_incidents[merged_incidents._merge == 'left_only'].COUNTY_NAME.unique()

# %%
# merge all incidents to all offenses to get the offense category name
# ***there can be multiple offenses per incident***
merged_crimes = pd.merge(merged_incidents.drop('_merge', axis=1),merged_offenses[['INCIDENT_ID','OFFENSE_CATEGORY_NAME']],on='INCIDENT_ID', how='left', indicator=True, validate='m:m')

# %%
# grab month out of incident date to be used for aggregation
merged_crimes["month"] = merged_crimes.INCIDENT_DATE.str[3:6]

# %%
# create list of what are considered violent crimes
violent_crimes = ['Burglary/Breaking & Entering','Assault Offenses','Arson','Robbery','Sex Offenses','Animal Cruelty','Homicide Offenses','Kidnapping/Abduction','Sex Offenses, Non-forcible','Human Trafficking']

# %%
# check cases where an incident falls in both violent and non-violent categories
violent_incidents = merged_crimes[merged_crimes["OFFENSE_CATEGORY_NAME"].isin(violent_crimes)].INCIDENT_ID
non_violent_incidents = merged_crimes[~merged_crimes["OFFENSE_CATEGORY_NAME"].isin(violent_crimes)].INCIDENT_ID
both_v_and_nonv = merged_crimes[merged_crimes["INCIDENT_ID"].isin(violent_incidents) & merged_crimes["INCIDENT_ID"].isin(non_violent_incidents)].INCIDENT_ID.unique()

# %%
# create new column to identify crime as violent(1) or non-violent(0)
merged_crimes["violent_crime"] = 1
merged_crimes.loc[~merged_crimes["INCIDENT_ID"].isin(both_v_and_nonv) & merged_crimes["INCIDENT_ID"].isin(non_violent_incidents), "violent_crime"] = 0

# %%
merged_crimes["duplicated_incident"] = merged_crimes.duplicated(subset=['INCIDENT_ID'])

# %%
# create new column to aggreagrate all incidents
merged_crimes["crime_count"] = np.where(merged_crimes["duplicated_incident"] == False, 1, 0)

# %%
# aggregate crimes by month, year, fips code, and offense category name
final_crimes = merged_crimes.groupby(["month","DATA_YEAR","fips","OFFENSE_CATEGORY_NAME","violent_crime"]).agg({"crime_count":"sum"}).reset_index()

# %%
# aggregate crimes by month, year, fips code, and whether it is a violent crime
final_crimes.groupby(["month","DATA_YEAR","fips","violent_crime"]).agg({"crime_count":"sum"}).reset_index()

# %%
# grab only the first three letters of the month column in pop data
pop["month"] = pop.month.str[0:3].str.upper()

# %%
# change it to an integer for merging
pop["DATA_YEAR"] = pop.year.astype(int)

# %%
# merge population data to get population for each fips code
merged_pop = pd.merge(final_crimes,pop.drop(['year','fips_state_county_code'], axis=1), on=["fips","month","DATA_YEAR"], how="inner")

# %%
# create a new column to calculate the crime rate per 100,000 people
merged_pop["crime_rate"] = (merged_pop.crime_count/merged_pop.population)*100000

# %%
# push merged_pop table to repo as csv
merged_pop.to_csv("/mnt/c/Users/sdona/Documents/Duke/22Spring/701IDS/FinalProject/uds-2022-701-team-5/20_intermediate_files/crime_rate.csv", index=False)


