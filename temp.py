'''
practicing sending and recieving model data with web form

NOTE: I moved this over to the predict_salary.py file.
        We can delete this file as soon as everything is working.
        -kelsey --3/14/20
'''
import pandas as pd
import numpy as np


def model_run(txt_pathway, state, edu, exp):
    '''
    Handles data from the UI and returns a response to the user.
    '''

    x_vector = input_to_dummies(txt_pathway, state, edu, exp)



def input_to_dummies(txt_pathway, state, edu, exp):
  '''
  Transforms ui text data into a vector to send to predictive model.
  '''
  career_base_data = pd.read_csv('data_files/career_pathways.csv')
  dummies_df = pd.read_csv('data_files/dummies.csv',nrows = 1)
  dummy_col = dummies_df.columns[1:]
  row = pd.DataFrame(data = [[0] * len(dummy_col)],
    columns = dummy_col.tolist())

  pathway_text = career_base_data['career_pathway'][int(txt_pathway)]
  pathway_text = 'career_pathway_' + pathway_text
  state_text = 'state_' + state

  educ_dict = {'0':'below_BA_req',
               '1':'below_BA_req',
               '2':'BA_req',
               '3':'MA_req',
               '4':'above_MA_req'
               }

  exp_dict = {'0':'min_yrs_exp_<1',
              '1':'min_yrs_exp_1-1.9',
              '2':'min_yrs_exp_2-3.9',
              '3':'min_yrs_exp_>=4'}

  row[pathway_text][0] = 1
  row[state_text][0] = 1
  row[educ_dict[edu]][0] = 1
  row[exp_dict[exp]][0] = 1

  return row
