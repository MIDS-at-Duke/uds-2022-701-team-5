This is the repository for Team 5's final project for the course IDS 701 Unifying Data Science.

# Estimating the Impact of Support Team Assisted Response in Denver, Colorado

Contributors: Aarushi Verma, Cindy Chiu, Dauren Bizhanov, Sydney Donati-Leach

## Project Outline

In Denver, Colorado, there is an emergency service known as Support Team Assisted Response (STAR). The STAR experiment was implemented on June 1, 2020 to provide assistance when someone calls 9-1-1 for something like a mental health crisis, substance use issue or even incidents like homelessness or public intoxication. The 9-1-1 operator can dispatch a STAR team to the scene which includes a licensed behavioral health professional and a paramedic. The city is citing growing success with the program and is looking to expand it. The purpose of this analysis is to corroborate these reports of success by looking at how STAR has impacted non-violent arrest rates in Denver, Colorado.  We will do this using the causal inference approach of a difference-in-difference regression analysis.

## Data

We obtained data for both national crime and arrests to calculate the number of non-violent arrests and the number of non-violent crime incidents that took place within our timeframe of interest. Since there is no single source data that contains both crime and arrest rates, we obtained the data from two different sources and conducted analysis separately on both data.
- [Crime Data](https://www.fbi.gov/services/cjis/ucr/nibrs)
- [Arrest Data](https://www.fbi.gov/services/cjis/ucr/)

## Trend Analysis

We used Denver county as our treatment group and the other counties in the Denver metro area as our control group (listed below).
- Adams
- Arapahoe
- Boulder
- Broomfield
- Douglas
- Jefferson

To accurately examine the causal effect of the STAR program, the non-violent arrest rates before the program was implemented should be parallel between the treatment and the control groups. We met the parallel trends assumption, which can be seen in this [plot](https://github.com/MIDS-at-Duke/uds-2022-701-team-5/blob/main/30_results/Plots/Arrest_prepolicy_NonV.png).

## Regression Results

We ran multiple regressions where the independent variable was a demographic subgroup. This was necessary because of the structure of the arrest data. The data did not provide arrests on an individual level, but instead were pre-aggregated into demographic subgroups. Therefore, we could not add these variables as features in one model, and instead opted to model each of them separately. We also included county and month fixed effects into each regression. For the placebo test we limited the data to only the pre-implementation time period of January 1, 2019, to May 30, 2020. The simulated implementation date we chose was January 1, 2020.

- [Placebo Test](https://github.com/MIDS-at-Duke/uds-2022-701-team-5/blob/main/30_results/placebo_test.csv)
- [Difference-in-Difference Model](https://github.com/MIDS-at-Duke/uds-2022-701-team-5/blob/main/30_results/regression_results.csv)

## Project Deliverables
The detailed research paper can be found [here](https://github.com/MIDS-at-Duke/uds-2022-701-team-5/tree/main/40_report)

The video of our project presentation can be found [here](https://www.youtube.com/watch?v=Ni_V17Q0_P0)
