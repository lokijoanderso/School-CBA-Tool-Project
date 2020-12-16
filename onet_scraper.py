'''
Web Scrapper for O*NET Career Information
(kelsey anderson)

Module to identify and download information from O*NET online
data source for use in education-career model creation.

Uses downloaded csv of all job titles by career cluster and career pathway
as a starting point (source: https://www.onetonline.org/find/career?c=0&g=Go
accessed 02/17/2020).

NOTE: Full scrape of all 1110 job titles in the default csv file takes
    a very long time to complete. For testing purposes, running file defaults
    to SMALL_DATA_SET of 25 codes for testing purposes.

Creates a csv output with columns:

- soc_8_digit (string): full formatted soc code from O*NET
- soc (6 digit string): verison used by BLS data
- soc_plus_2 (2 digit string, usually "00"): specific sub-job titles
- job_title (string): English language job title
- career_cluster (string): highest level grouping
- career_pathway (string): mid-level job grouping
- other_titles (list): other commonly used verisons of job title
- min_yrs_exp (float ranging from 0.0 - 10.0):
    calculated from lower bound on SVP field
    model should exclude people with this amount of years work experience
    or less from qualifying for job. None if unavailable.
- nat_wage (float): 0.00 if unavailable.
- less_than_high_school_diploma (int): percent of workforce with this education
- high_school_diploma (int): percent of workforce with this education
- certificate (int): percent of workforce with this education
- some_college (int): percent of workforce with this education
- associates_degree (int): percent of workforce with this education
- bachelors_degree (int): percent of workforce with this education
- post_bacc_certificate (int): percent of workforce with this education
- masters_degree (int): percent of workforce with this education
- post_masters_certificate (int): percent of workforce with this education
- first_professional_degree (int): percent of workforce with this education
- doctoral_degree (int): percent of workforce with this education
- post_doctoral_training (int): percent of workforce with this education

'''

import csv
import bs4
import json
import requests
import re
import pandas as pd

BASE_CSV_FILE_PATH = "data_files/All_Career_Clusters.csv"
SMALL_DATA_SET = "data_files/25_career_clusters.csv"
BASE_JOB_DATA_URL = "https://www.onetonline.org/link/details/"
OUTPUT_FILE_PATH = "data_files/onet_data.csv"

# designated min years of experience
SVP_DICT = { "0.0": None,
             "1.0": 0.0,
             "2.0": 0.01,
             "3.0": 0.08,
             "4.0": 0.25,
             "5.0": 0.5,
             "6.0": 1.0,
             "7.0": 2.0,
             "8.0": 4.0,
             "9.0": 10.0 }

# headers for data file
COL_NAMES = ["soc_8_digit", "soc", "soc_plus_2", "job_title",
             "career_cluster", "career_pathway",
             "min_yrs_exp", "nat_wage"]

EDUC_COL_NAMES = ['less_than_a_high_school_diploma',
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
                  'post-doctoral_training']


def run_full_dataset(data=SMALL_DATA_SET,
                     output_location=OUTPUT_FILE_PATH):
    '''
    Runs through all job titles downloaded from the career clusters
    O*NET webpage (https://www.onetonline.org/find/career?c=0&g=Go)
    and scrapes additional requirements data from
    each individual O*NET details page.

    Input: 
        base_data (string file pathway):
            defaults to full csv downloaded from O*NET
            with information on 1110 job titles.
        output_location (string file pathway):
            defaults to shared project folder's
            "data_files/onet_data.csv" location

    Returns: None, but prints a csv file of all captured data
        to specified or default location.
    '''

    base_data = create_base_list(data)

    with open(output_location, "w") as file:
        file_writer = csv.writer(file, delimiter=",")
        file_writer.writerow(COL_NAMES + EDUC_COL_NAMES)

        for data in base_data.itertuples():
            soup_obj = read_soc_page(data.soc_8_digit)

            if soup_obj:
                soc_dict = extract_soc_data(soup_obj)
                output = build_output_row(base_data.loc[data.Index], soc_dict)

                print("saving data... " + str(output[0]) + " " + str(output[5]))
                file_writer.writerow(output)


def create_base_list(csv_pathway):
    '''
    Takes a download from the O*NET website of codes and job titles
    to build additional data on top of with webscraper.

    Input: csv_pathway (string): file location of csv download

    Returns: pandas dataframe with columns (all string):
        - career_cluster
        - career_pathway
        - soc_8_digit
        - job_title
        - soc (the 6 digit code used elsewhere)
        - soc_plus_2 (additional granularity on title)
    '''
    header_names = ["career_cluster","career_pathway",
                    "soc_8_digit","job_title"]

    soc_base = pd.read_csv(csv_pathway, header=0, names=header_names)

    soc_base["soc"] = soc_base["soc_8_digit"].str.replace("-","").str[0:6]
    soc_base["soc_plus_2"] = soc_base["soc_8_digit"].str[8:]

    return soc_base


def read_soc_page(soc_8_digit):
    '''
    Using requests and beautiful soup, retrieve a scraped webpage
    from O*NET for the job code input.

    Inputs: soc_8_digit (string): a job code in the format "00-0000.00"

    Returns: a beautiful soup object representation of webpage
    '''
    url = BASE_JOB_DATA_URL + soc_8_digit

    try:
        url_request = requests.get(url)

        if url_request.status_code != requests.codes.ok:
            url_request = None

    except Exception:
        url_request = None

    if url_request:

        url_soup = bs4.BeautifulSoup(url_request.text)

        return url_soup
    return None


def extract_soc_data(bs4_soc_page):
    '''
    Runs through the beautiful soup representation of a job details
    page from O*NET and extracts the data (if any) at:
        - Other job titles
        - SVP code --> translated to minimum years of experience
        - education levels (12 columns with percent of workers each)
        - projected national wage

    Inputs:
        bs4_soc_page (bs4 object): the O*NET job details page

    Returns:
        soc_data (dictionary): a dictionary of the the data listed above
    '''
    soc_data = {}

    # get minimum years experience
    svp_text = bs4_soc_page.find("div", id="wrapper_JobZone")
    if svp_text:
        svp_text = svp_text.find_all("td", class_="report2")[-1].text
        svp = re.search(r"([0-9]+\.0)", svp_text).group(0)
    else:
        svp = "0.0"

    soc_data["min_yrs_exp"] = SVP_DICT[svp]

    # get education level percents
    educ_dict = {}
    table_title = "Education information for this occupation"

    edu_section = bs4_soc_page.find("table", summary=table_title)

    if edu_section:
        edu_levels =  edu_section.find_all("td", class_="report2")
        edu_percents = edu_section.find_all("td", class_="report2a")

        for index, level in enumerate(edu_levels):
            percent = edu_percents[index].text.strip()

            if percent == "Not available":
                percent = 0

            educ_dict[level.text.strip().lower().replace(" ", "_") \
                      .replace("'","")] = int(percent)

    soc_data["education"] = educ_dict

    # get projected job openings & growth category
    table_title = "Wages & Employment Trends information for this occupation"

    projection_section = bs4_soc_page.find("table", summary=table_title) 

    if projection_section:
        job_projections = projection_section.find_all("td", class_="report2")
        
        if job_projections[1].text:
            soc_data["nat_wage"] = float(job_projections[0].text[1:5])
        else:
            soc_data["nat_wage"] = 0.00

    return soc_data


def build_output_row(base_row, soc_dict):
    '''
    Writes a list of values to be printed to datafile
    for one job. This function merges the originally
    extracted csv data download with the data dictionary scraped.

    Inputs:
        base_row (dataframe row): a pandas row for the job to be written.
        soc_dict: a dictionary of scraped data for that job.

    Returns:
        A list with each row of data to be output as one item. 
    '''
    output = []

    for col_name in COL_NAMES:
        if col_name in base_row.index:
            output.append(base_row[col_name])
        else:
            output.append(soc_dict[col_name])

    for educ_level in EDUC_COL_NAMES:
        output.append(soc_dict["education"].get(educ_level, 0))

    return output



if __name__ == '__main__':
    run_full_dataset(SMALL_DATA_SET, "data_files/test_onet_data.csv")
    

