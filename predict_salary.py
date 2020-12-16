'''
Model class for predicting wage based on degree level
'''

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split


class Matcher:

    def __init__(self, dataset=pd.read_csv("data_files/dummies.csv")):
        
        self.df_law = pd.read_csv("data_files/best_law_schools.csv")
        self.df_eng = pd.read_csv("data_files/best_engineering_school.csv")
        self.df_bus = pd.read_csv("data_files/best_business_school.csv")
        self.dataset = dataset
        self.yvar = dataset.loc[:, "wage"].values
        self.xvar = dataset.drop("wage", axis=1).values
        


    def predict(self, user_data, xvar, yvar):
        
        x_train, x_test, y_train, y_test = train_test_split(self.xvar, self.yvar, test_size=0.4, random_state=0)
        lin_reg = LinearRegression()
        lin_reg.fit(x_train, y_train)

        x = np.asscalar(lin_reg.predict(user_data)[0])

        return x

    def data_fliter(self, mdegree):

        if mdegree == False:
            under_master = self.dataset[(self.dataset['MA_req'] == 0) & (self.dataset['above_MA_req'] == 0)]
            y = under_master.iloc[:,[0]].values
            x = under_master.iloc[:, 1:].values
        else:
            above_master = self.dataset[(self.dataset['MA_req'] == 1) | (self.dataset['above_MA_req'] == 1)]
            y = above_master.iloc[:,[0]].values
            x = above_master.iloc[:, 1:].values
        return y, x


    def find_wage(self, user_data):

        if (user_data.loc[0, 'MA_req'] == 1 or user_data.loc[0, 'above_MA_req'] == 1):
            y, x = self.data_fliter(mdegree = True)
            user_wage = self.predict(user_data.values,x, y)

        else:
            y, x = self.data_fliter(mdegree = True)
            user_wage = self.predict(user_data.values, x, y)

        r = user_wage * 261 * 8
        
        return r


    def matcher(self, user_data):

        if (user_data.loc[0, 'MA_req'] == 1 or user_data.loc[0, 'above_MA_req'] == 1):
            return [self.find_wage(user_data)]

        else:
            current_wage = self.find_wage(user_data)
            user_data.loc['MA_req'] = 1
            user_data['BA_req'] = 0
            user_data['above_MA_req'] = 1
            user_data['below_BA_req'] = 0
            pred_wage = self.find_wage(user_data)
            pd.to_numeric(self.df_bus['Tuition'])
            return [current_wage, pred_wage]


            
'''
Functions to send and return data from the UI and model
'''

def run_model(txt_pathway, state, edu, exp):
    '''
    Handles data from the UI and returns a response to the user.
    '''

    model = Matcher()

    x_vector = input_to_dummies(txt_pathway, state, edu, exp)
    predicted = model.matcher(x_vector)

    return predicted


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
