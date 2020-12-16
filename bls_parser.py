'''
BLS Data Parser

Kelsey Anderson & Yawei Li

Currently python bls_parser.py will run a test to parse a sample of data
of around 20 rows. This script is fully able to parse the entire needed
dataset in a reasonable amount of time. (8000 rows)

Due to limitations of BLS API, the complete parsing has to be done using
two keys or seperated in two days, and will take a rather long time and multiple
calls which isn't fit for grading purposes. 

Full pre-parsed dataset is stored in 'data_files/wage_job_state.csv' 

'''

import requests
import json
import pandas as pd
import csv

# number of jobs to send to the API at a time
BATCHES = 10

API_KEY = "d11f41d97d764bb5bcc6bb2f84b368e2"

STATES_FILE = "data_files/bls_area_codes.csv"
SOC_FILE = "data_files/onet_data.csv"

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# Constructing Series IDs, nums below indicate their position in the
# constructed Series ID, which is used to find desired dataset.
PREFIX = 'WMU' # 1-3
OWNER_ESTIMATE = '102' #11-13
INDUSTRY = '000000' #14-19
JOB_CHAR = '25' #26-27 full time
JOB_LEVEL = '00' # All


# Constructing State Codes and Job Codes
def read_csv_data(state_data_location, soc_code_location):
    '''
    Reads in the csv files from onet and bls for the codes
    needed to create bls data API requests.

    Also returns dictionaries for text value lookups.
    '''

    states = pd.read_csv(STATES_FILE, dtype=str)
    socs = pd.read_csv(SOC_FILE, dtype=str)

    states.set_index("area_code", inplace=True)
    socs.set_index("soc", inplace=True)

    states_list = states.index.tolist()
    soc_list = socs.index.tolist()

    occupation_dict = socs["job_title"].to_dict()
    state_dict = states["State_Abbrv"].to_dict()

    return (states_list, soc_list, state_dict, occupation_dict)


# Constructing SIDs (state/job strings to request bls data)
def build_output_file(states, soc_codes,
                      state_dict, occ_dict,
                      num_of_batches= 1, new_file=False,
                      out_file = 'data_files/wage_job_state_test.csv',
                      used_file = 'data_files/processed_codes.csv'):
    '''
    Takes a list of all states and soc codes and
    creates the request strings for every job in every state. (50)
    Since requests also batched 50 at a time. (API Limitation)

    out_file and used_file can be specified to fit testing or full
    parsing purposes.

    '''
    batch_counter = 0

    headers = {'Content-type': 'application/json'} 
    data = {"seriesid":[], "latest":"true",
                        "registrationkey": API_KEY}
    nrecords = 0
    nempty = 0
    
    try:
        pre_processed = pd.read_csv(used_file, dtype=str)

    except:
        pre_processed = pd.DataFrame({"used": [""]})


    with open(out_file,'a') as f:
        csv_writer = csv.writer(f, delimiter = ',')
        
        if new_file:
            output_header = ["soc", "title", "area_code", "state", "wage"]
            csv_writer.writerow(output_header)

        job_list = []

        for job in soc_codes:

            while batch_counter < num_of_batches:
                if job in pre_processed["used"].values or job in job_list:
                    break

                else:
                    job_list.append(job)

                sid_list = []
   
                for state in states:
                
                    sid_list.append(PREFIX + state + OWNER_ESTIMATE
                                   + INDUSTRY + job + JOB_CHAR + JOB_LEVEL)

                data["seriesid"] = sid_list
        
                r = requests.post(BLS_URL, data=json.dumps(data), headers=headers)
                r_dict = json.loads(r.text)

                batch_counter += 1

                for result in r_dict['Results']['series']:
                    sid = result["seriesID"]

                    if len(result['data']) == 0:
                        nempty += 1

                    else:
                        area = sid[3:10]
                        soc = sid[19:25]
                        wage = result['data'][0]['value']

                        nrecords += 1
                        row = [soc, occ_dict[soc], area, state_dict[area], wage]
                    
                        csv_writer.writerow(row)  

        all_used = pre_processed['used'].tolist() + job_list
        pd.Series(all_used).to_csv(used_file, index=False, header=["used"])
        print(str(nrecords) + " wage observation stored in " + out_file)
        print(str(nempty) + " records are empty")

def test():
    '''
    Run a test for this parser.
    '''
    state_list, soc_list, state_dict, occ_dict = read_csv_data(STATES_FILE,
                                                                SOC_FILE)

    build_output_file(state_list, soc_list, state_dict, occ_dict, BATCHES)


    print(str(BATCHES) + " batches of 50 records complete")


if __name__ == '__main__':
    test()
