'''
Feature Table
(kelsey anderson, yawei li)

Pull extracted data together into a single feature table for
model analysis.

Uses csv files in data_files directory:
    - onet_data.csv
    - wage_job_state.csv

'''
import pandas as pd


ONET_DATA = "data_files/onet_data.csv"
WAGE_DATA = "data_files/wage_job_state.csv"

EDUC_REQ_THREASHOLD = 25

STATE_DICT = {"Alabama": "AL",
              "Alaska": "AK",
              "Arizona": "AZ",
              "Arkansas": "AR",
              "California": "CA",
              "Colorado": "CO",
              "Connecticut": "CT",
              "Delaware": "DE",
              "Florida": "FL",
              "Georgia": "GA",
              "Hawaii": "HI",
              "Idaho": "ID",
              "Illinois": "IL",
              "Indiana": "IN",
              "Iowa": "IA",
              "Kansas": "KS",
              "Kentucky": "KY",
              "Louisiana": "LA",
              "Maine": "ME",
              "Maryland": "MD",
              "Massachusetts": "MA",
              "Michigan": "MI",
              "Minnesota": "MN",
              "Mississippi": "MS",
              "Missouri": "MO",
              "Montana": "MT",
              "Nebraska": "NE",
              "Nevada": "NV",
              "New Hampshire": "NH",
              "New Jersey": "NJ",
              "New Mexico": "NM",
              "New York": "NY",
              "North Carolina": "NC",
              "North Dakota": "ND",
              "Ohio": "OH",
              "Oklahoma": "OK",
              "Oregon": "OR",
              "Pennsylvania": "PA",
              "Rhode Island": "RI",
              "South Carolina": "SC",
              "South Dakota": "SD",
              "Tennessee": "TN",
              "Texas": "TX",
              "Utah": "UT",
              "Vermont": "VT",
              "Virginia": "VA",
              "Washington": "WA",
              "West Virginia": "WV",
              "Wisconsin": "WI",
              "Wyoming": "WY"}


def combine_job_and_wage_data(onet_data=ONET_DATA, wage_data=WAGE_DATA):
    '''
    merges and cleans scraped job and wage data.
    '''
    jobs = pd.read_csv(onet_data, dtype=str)
    wages = pd.read_csv(wage_data, dtype=str)

    for num in range(10, 22):
        jobs[jobs.columns[num]] = jobs[jobs.columns[num]].astype(int)

    jobs["min_yrs_exp"] = jobs["min_yrs_exp"].astype(float)

    # separate format "Chicago, IL" into a state == 'IL' column
    wages = wages.rename(columns={wages.columns[2] : "soc"})

    # add state abbreviations and drop any non-US state observations
    wages["state"] = wages["Area text"].map(STATE_DICT)
    wages = wages[wages.state.notna()]

    # combine and drop observations with nulls in feature table fields
    combined = pd.merge(jobs, wages, how="inner", on="soc")

    combined["Average hourly wage"] = combined["Average hourly wage"] \
                                        .str.replace("-", "0").astype(float)
    combined = combined[combined["Average hourly wage"] > 0.0]
    combined = combined[combined.min_yrs_exp.notna()]

    # make naming more consistent
    combined = combined.rename(columns={"Average hourly wage": "wage"})

    # updating a list of careers to allow the user to pick in the UI
    menu_opts = combined[["career_cluster", "career_pathway"]]

    menu_opts = menu_opts.groupby("career_pathway", as_index=False) \
        ["career_cluster"].max().sort_values(by=["career_cluster"])

    menu_opts.to_csv("data_files/career_pathways.csv", index=False)

    return combined


def build_feature_table(cleaned_data):
    '''
    Reduce and catagorize dataframe with extracted data into
    a feature table for use by CBA model.

    '''

    # career path with avg wage and tuition per educ/exp level per state
    working = cleaned_data[["state", "career_pathway", "min_yrs_exp", "wage",
                             'less_than_a_high_school_diploma',
                             'high_school_diploma_or_equivalent',
                             'post-secondary_certificate',
                             'some_college_courses',
                             'associates_degree',
                             'bachelors_degree',
                             'post-baccalaureate_certificate',
                             'masters_degree',
                             'post-masters_certificate',
                             'first_professional_degree',
                             'doctoral_degree',
                             'post-doctoral_training']] \
                             .groupby(["state", "career_pathway", "min_yrs_exp"],
                                      as_index=False).mean()

    # sum and create categories for education level
    edu_bin = [0, EDUC_REQ_THREASHOLD, float("inf")]

    working["above_MA_req"] = working[['post-masters_certificate',
                                       'doctoral_degree',
                                       'post-doctoral_training']].sum(axis=1)
    
    working["above_MA_req"] = pd.cut(working["above_MA_req"],
                                     bins=edu_bin,
                                     labels=[0,1], include_lowest=True)

    working["MA_req"] = working[['first_professional_degree',
                                 'post-baccalaureate_certificate',
                                 'masters_degree']].sum(axis=1)

    
    working["MA_req"] = pd.cut(working["MA_req"],
                               bins=edu_bin,
                               labels=[0,1], include_lowest=True)

    working["BA_req"] = working[['bachelors_degree']].sum(axis=1)

    working["BA_req"] = pd.cut(working["BA_req"],
                               bins=edu_bin,
                               labels=[0, 1], include_lowest=True)

    working["below_BA_req"] = working[['less_than_a_high_school_diploma',
                                       'high_school_diploma_or_equivalent',
                                       'post-secondary_certificate',
                                       'some_college_courses',
                                       'associates_degree']].sum(axis=1)
    
    working["below_BA_req"] = pd.cut(working["below_BA_req"],
                                     bins=edu_bin,
                                     labels=[0, 1], include_lowest=True)
    # cat for min yrs exp
    working["min_yrs_exp"] = pd.cut(working["min_yrs_exp"],
                                    bins=[0.0, 1.0, 2.0, 4.0, 11.0],
                                    labels=["<1", "1-1.9", "2-3.9", ">=4"],
                                    include_lowest = True, right = False)

    feature_table = working[["state", "career_pathway", "min_yrs_exp",
                              "wage", "below_BA_req", "BA_req", "MA_req",
                              "above_MA_req"]]

    return feature_table


def dummy_table(ft):
  '''
  Create a dummied feature table from given feature table with desired
  column names.
  '''
  dummies = pd.get_dummies(ft,columns = ['state','career_pathway',
    'min_yrs_exp'])

  return dummies


def main():
    '''
    Auto-create dummy table for model
    '''
    combined_df1 = combine_job_and_wage_data()
    feature_table = build_feature_table(combined_df1)
    dummies = dummy_table(feature_table)
    dummies.to_csv('data_files/dummies.csv',index = False)

    return dummies


if __name__ == '__main__':
    main()


