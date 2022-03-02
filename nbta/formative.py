from typing import DefaultDict
from termcolor import colored
import numpy as np
import pandas as pd
import pickle 

class NBTest:
    def __init__(self,testName='test',**kwargs):
        self.testName = testName
        self.variables = kwargs
        self.results = []
        self.noProblems = True
    
    def setup(self):
        self.setupFromFile(f'{self.testName}.cvs')
        return self

    def setupFromFile(self, filename):
        testData = pd.read_csv(filename)

        for index, item in testData.iterrows():
            try:
                data = {'result':self.variable.get(item[0]),
                'expected':item[1],
                'error_message':item[2]}
                self.results.append(data)
            except:
                pass
        
        
    def run(self):
        pass
    
    def generateString(self, items):
        text=f'CHECKING AND SAVING VARIABLES FOR TEST "{self.testName}"'
        base_string = f"""
        \n======================================================================
        \n{colored(text, 'blue',attrs=['bold'])}"""
        
        substrings =  '\n----------------------------------------------------------------------\n'.join(items)
        return f"{base_string}{substrings}"
    
    def save_variable(self, variable, filename):
        outfile = open(f"answers/{filename}.pkl",'wb')
        data = [self.cid,variable]
        pickle.dump(data,outfile)
        outfile.close()
        
        return message


class CheckCode:
    def __init__(self,**kwargs):
        self.results = kwargs
        self.noProblems = True
        
    def checkAll(self):
        messages = [self.checkSetup(),
                    self.checkPartA(),
                    self.checkPartB(),
                    "\n======================================================================"]
        if self.noProblems:
            messages.append(colored('\nALL GOOD - PUSH TO GITHUB\n', 'green',attrs=['bold','underline']))
            messages.append(colored('\nRemember to run this cell again if you change your code\n', 'magenta',attrs=['bold','underline']))
        else:
            messages.append(colored('\nTHERE ARE SOME POTENTIAL PROBLEMS WITH YOUR CODE', 'magenta',attrs=['bold','underline']))
        return '\n'.join(messages)
        
    def checkSetup(self):
        cid = self.results['cid']
        self.cid = cid
        username = self.results['username']
        items = ['\n']
        
        items.append(self.test_type(cid,'cid','INTEGER','the setup section'))
        items.append(self.test_type(username,'GitHubUsername','STRING','the setup section'))
        
        return self.generateString('GENERAL SETUP',items)
    
    def checkPartA(self):
        items = ['\n']
        
        types = [(self.results['cdf_nb_missing'],'cdf_nb_missing', 'INTEGER', 'Question 1 (a)'),
        (self.results['cdf_std_mean'], 'cdf_std_mean', "FLOAT", 'Question 1 (b)'),
        (self.results['cdf_min_carb'], 'cdf_min_carb', "FLOAT", 'Question 1 (c)'), 
        (self.results['cdf_max_carb'], 'cdf_max_carb', "FLOAT", 'Question 1 (c)'),
        (self.results['num_columns'], 'num_columns', 'Numpy Array', 'Question 2'),
        (self.results['outliers_present'], 'outliers_present', 'STRING', 'Question 4')
        ]
        
        items = items + [self.test_type(var,name,typ,loc) for var,name,typ,loc in types]
        
        dfs = [(self.results['core_df'],'core_df', 'Questions 1-4'),
        (self.results['encoded_df'],'encoded_df', 'Question 5'),]
        items = items + [self.test_dataframe(var,name,loc) for var,name,loc in dfs]
        
        return self.generateString('PART A',items)
        return ''
    
    def checkPartB(self):
        types = [(self.results['final_model'],'final_model', 'LogisticRegression()', 'Question 6'),
                 (self.results['predictions'],'predictions', 'Numpy Array', 'Question 6')]
        
        items = ['\n'] + [self.test_type(var,name,typ,loc) for var,name,typ,loc in types]
        
        return self.generateString('PART B',items)
    
    def generateString(self, part, items):
        text=f'CHECKING AND SAVING VARIABLES IN {part}'
        base_string = f"""
        \n======================================================================
        \n{colored(text, 'blue',attrs=['bold'])}"""
        
        substrings =  '\n----------------------------------------------------------------------\n'.join(items)
        return f"{base_string}{substrings}"
    
    def save_variable(self, variable, filename):
        outfile = open(f"answers/{filename}.pkl",'wb')
        data = [self.cid,variable]
        pickle.dump(data,outfile)
        outfile.close()
    
    def test_dataframe(self, df, df_name, question):
        message = ''
        if type(df) == pd.DataFrame:
            message = f"A Pandas DataFrame named {df_name} exists: {colored('PASSED', 'green',attrs=['bold','underline'])}"       
        else:
            problem = f"{df_name} is not a pandas DataFrame: {colored('FAILED', 'red',attrs=['bold','underline'])}"
            suggestion = f'SUGGESTION:Check in "{question}" that you have saved your {df_name} as a DataFrame (instead of e.g. a Numpy array)'
            suggestion = colored(suggestion, 'yellow')
            message = '\n'.join([problem, suggestion])
            self.noProblems = False
        try:
            self.save_variable(df,df_name)
            message = f"{message}\n{colored(f'Content of {df_name} correctly saved', 'green')}" 
        except:
            message = f"{message}\n{colored('Unable to save data from the dataframe', 'red')}" 
        return message
            
    def test_type(self, variable, variable_name, expected_type, question):
        type_to_str = {
            int:'INTEGER',
            str:'STRING',
            float:'FLOAT',
            object:'OBJECT',
            np.int64:'INTEGER',
            np.float64:'FLOAT',
            np.ndarray: 'Numpy Array',
            LogisticRegression:'LogisticRegression()'
        }
        
        variable_type = type_to_str[type(variable)]
        message = ''
        suggestion = ''
        
        if variable_type == expected_type:
            message = f"{variable_name} exists and is of type {variable_type}: {colored('PASSED', 'green',attrs=['bold','underline'])}"
        else:
            problem = f"{variable_name} is of type {variable_type}: {colored('FAILED', 'red',attrs=['bold','underline'])}"
            suggestion = f'SUGGESTION:Check in "{question}" that the variable {variable_name} is of type {expected_type}'
            suggestion = colored(suggestion, 'yellow')
            message = '\n'.join([problem, suggestion])
            self.noProblems = False
            
        try:
            self.save_variable(variable,variable_name)
            suggestion = colored(f"Variable {variable_name} was saved as a pickle file", 'green')
            message = '\n'.join([message, suggestion])
        except Exception as e:
            message = f'{e}'
            suggestion = colored(f"Unable to save variable {variable_name} as a pickle file", 'red')
            message = '\n'.join([message, suggestion])
        
        return message
