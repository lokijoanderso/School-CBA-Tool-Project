'''
Fields for UI forms
'''

import pandas as pd
import sys
sys.path.append('../')
from feature_table import STATE_DICT


educ_levels = [("0", "High School Graduate or Below"),
               ("1", "Some College or Associate Degree"),
               ("2", "Bachelor's Degree"),
               ("3", "Master's Degree"),
               ("4", "Higher than Master's Degree")
               ]

exp_levels = [("0", "Less than one year"),
              ("1", "1 year to under 2 years"),
              ("2", "2 years to under 4 years"),
              ("3", "4 or more years")]

career_base_data = pd.read_csv("data_files/career_pathways.csv")


def build_career_opts():
    '''
    build and return a list of high level careers
    and subcareer pathways. Also returns a dictionary for decoding
    index code values.
    '''

    careers = []
    pathways = []
    link = {}
    temp_link = {}

    counter = 0

    for index, (pathway, career) in career_base_data.iterrows():
        if career not in careers:
            careers.append(career)
        
        temp_link[career] = temp_link.get(career, []) + [str(index)]

        pathways.append((str(index), pathway))
        counter +=1

    counter = 0
    careers = []
    for key, lst in temp_link.items():
      link[str(counter)] = lst
      careers.append((str(counter), key))
      counter +=1

    careers.sort(key = lambda x: x[1])

    return (careers, pathways, link)

def build_state_opts():
    '''
    call the state dictionary from feature table module
    and return the keys to a list.
    '''
    states = []
    for state, abbv in STATE_DICT.items():
      states.append((abbv, state))

    states.sort()
    return states