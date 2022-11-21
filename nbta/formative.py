from typing import DefaultDict
from termcolor import colored
import numpy as np
import pandas as pd
import pickle 
import numpy as np
import pandas as pd
from os import listdir
from wordcloud import WordCloud, STOPWORDS
from IPython.display import display
import matplotlib.pyplot as plt
from IPython.core.display import HTML
from termcolor import colored

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

class QuizCheck():
    '''
    QuizCheck offers a class to provide visual feedbacks on small quizes conducted through Google Forms.
    '''
    def __init__(self, path, answer_file=None):
        self.path = path
        self.answers = self.build_dataframe(path)
        self.correct_answers = False
        if answer_file:
            self.correct_answers = pd.read_excel(f'{path}/{answer_file}')
      
        self.questions = self.get_questions(self.answers)
        display(HTML(f'<h2>Number of questions:{len(self.questions)}</h2>'))
    
    def build_dataframe(self, path):
        forms = [form for form in listdir(path) if form.split('.')[-1]=="csv"]
        forms.sort()
        df = pd.read_csv(f'{path}/{forms[0]}')
        for form in forms[1:]:
            df = pd.concat([df,pd.read_csv(f'{path}/{form}')])
        return df
     
    def get_questions(self, df):
        allColumns = list(df.columns)
        allColumns.remove('Timestamp')
        allColumns.remove('Total score')
        return [question for question in allColumns if question.find(' [Score]') ==-1 if question.find(' [Feedback]') ==-1]
    
    def split_answers(self, answer):
        return answer.split(';')
    
    def num_to_words(self, num):
        dic = {
            0:'zero',
            1:'one',
            2:'two',
            3:'three',
            4:'four',
            5:'five',
            6:'six',
            7:'seven',
            8:'eight',
            9:'nine'
        }

        try:
            num=int(float(num))
            return dic.get(num, 'many')
        except:
            return num


    def draw_WordCloud(self, question, image):
        fig, ax = plt.subplots(1,1, figsize=(15,8))
        ans = self.answers[question].dropna()
        text = " ".join(self.num_to_words(answer) for answer in ans.astype(str))
    
        # lower max_font_size, change the maximum number of word and lighten the background:
        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white", collocations=True).generate(text)

        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        fig.tight_layout(pad=6.0)
        #plt.rc('xtick',labelsize=10)
        #plt.rc('ytick',labelsize=30)
        plt.show()

    def format_numerical_answer(self, ans):
        ans = ans.dropna()
        nb_responses = len(ans)
    
        all_ans = []

        for value in ans.values:
            all_ans = all_ans+self.split_answers(value)
        ans = pd.Series(all_ans)

        data = ans.value_counts().sort_index(ascending=True)/nb_responses*100

        return data

    def draw_bars(self, question,  image):
        _, ax = plt.subplots(1,1, figsize=(9,9))
        ans = self.answers[question].dropna()
        nb_responses = len(ans)
    
        all_ans = []
        for value in ans.values:
            all_ans = all_ans+self.split_answers(value)
        ans = pd.Series(all_ans)
    
        data = ans.value_counts().sort_index(ascending=True)/nb_responses*100

        height = data.values
        x_pos = np.arange(len(height))
    
        # Create colors
        colors = []
        for bar in data.index:
            if bar in self.correct_answers[question].values:
                colors.append('green')
            else:
                colors.append('blue')
        
        # Create bars
        plt.bar(x_pos, height, color=colors)

        # Create names on the x-axis
        plt.xticks(x_pos, x_pos)
        plt.yticks(list(range(0,110, 10)))
        plt.ylabel('Percentage Answers', fontsize=14)
        plt.xlabel('Answer Number', fontsize=14)
        
        # Show graph
        plt.show()
    
        for i,label in enumerate(data.index):
            color=(0,0,0)
            if label in self.correct_answers[question].values:
                color= "green"   
            display(HTML(f'<font color={color}>{i}:{label}</font>'))
        return ax

    def answer(self, question_nb, correct_answers=[], image=None):
        question = self.questions[question_nb]
        display(HTML(f'<h2>{question}</h2>'))
        if self.answers[f'{question} [Score]'].dropna()[0][0] == '-':
            self.draw_WordCloud(question, image)
        else:
            self.draw_bars(question, image)
        display(HTML(f'<h3> <font color="blue">{" "*100}</font></h3>'))
        display(HTML(f'<h4> <font color="grey">{"_"*100}</font></h4>'))
        display(HTML(f'<h3> <font color="blue">{" "*100}</font></h3>'))
        plt.show()

    def print_answers(self):
        for nbq in range(len(self.questions)):
            self.answer(nbq)
    
    def get_percentage_right(self, given_answers):
        for question in self.questions:
            correct_answers = []
            if self.answers[f'{question} [Score]'].dropna()[0][0] == '-':
                pass
            else:
                data = self.format_numerical_answer(given_answers[question])
                correct_answers = correct_answers+[data[ans] for ans in data.index if ans in self.correct_answers[question].values]
        
        return sum(correct_answers)/len(correct_answers)
    
    def compare_scores(self, other_years=[]):
        bars = [self.get_percentage_right(self.answers)]
        labels = ['2022']
        colors = ['green']

        if len(other_years)!=0:
            for year in other_years:
                other_answers = self.build_dataframe(f'{self.path}/{year}')
                bars.append(self.get_percentage_right(other_answers))
                labels.append(str(year))
                colors.append('blue')

        _, ax = plt.subplots(1,1, figsize=(9,9))
        
        plt.bar(labels, bars, color=colors)

        plt.ylabel('Percentage Answers', fontsize=14)
        plt.xlabel('Year', fontsize=14)
        
        # Show graph
        plt.show()
            