import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import display, HTML
import os
from tqdm import tqdm

class NBTATest:
    def __init__(self,folder=None,**kwargs):
        self.results = kwargs
        self.folder = folder
        self.test_results = None

        if not os.path.exists('grades'):
                os.mkdir('grades')

    def run_test(self):
        pass

    def get_results(self):
        return self.test_results

class QuestionGrader:
    def __init__(self, question_name, options=None, auto_tests=None):
        self.base_dir = '../..'
        self.question_name = question_name
        self.auto_tests=auto_tests
        self.auto_tests_results={}


        if not os.path.exists('grades'):
                os.mkdir('grades')

        if self.auto_tests is not None:
            self.run_autotests()
        
        try:
            self.selected_values = pd.read_csv(f'grades/nbta_selection_{self.question_name}.csv')['options'].values
        except:
            self.selected_values = None
            
        try:
            self.selected_feedback = pd.read_csv(f'grades/nbta_feedback_{self.question_name}.txt')
        except:
            self.selected_feedback = None
        
        if options is None:
            self.options = self.read_options(f'{self.base_dir}/grading/testing/notebook_tests/{self.question_name}.csv')
        else:
            self.options = options
        
        self.autoresults = self.set_autoresults_widget()
        self.widgets = self.set_widgets()
        self.feedback = self.set_feedback()

        self.display()

    def run_autotests(self):
        for name, test in self.auto_tests.items():
            res = test.run_test()
            res_df = pd.DataFrame.from_dict(res,orient='index').T
            res_df.to_csv(f'grades/nbta_score_{name}.csv', index=False)
            self.auto_tests_results[name] = res_df
            
    def read_options(self, path):
        return pd.read_csv(path).options.values
    
    def set_widgets(self):
        content = []
        for option in self.options:
            this_value = False
            if self.selected_values is not None:
                if option in self.selected_values:
                    this_value = True
                
            w = widgets.Checkbox(value=this_value,
                description=option,
                disabled=False,
                indent=False)
            content.append(w)
        return content
    
    def set_autoresults_widget(self):
        display_results = []
        if self.auto_tests is not None:
            for test_name, results in self.auto_tests_results.items():
                lines = [f'[{test_name}] => ']+ [f'{k}: {v}' for k,v in results.items()]
                display_results.append(','.join(lines))
        display_results = '\n'.join(display_results)

        autoresults = widgets.Textarea(
            value=display_results,
            placeholder=display_results,
            description='Results from automatic tests:',
            disabled=True)
        
        return autoresults


    def set_feedback(self):
        if self.selected_feedback is not None:
            with open(f'grades/nbta_feedback_{self.question_name}.txt', 'r') as f:
                text = '\n'.join(f.readlines())
        else:
            text = ' '
        feedback = widgets.Textarea(
            value=text,
            placeholder=text,
            description='Feedback:',
            disabled=False)
        
        return feedback
    
    def display(self):
        display(HTML(f"<h2>AUTO TESTS {self.question_name}</h2>"))
        for test,df in self.auto_tests_results.items():
            display(HTML(f"<h3>{test.upper()}</h3>"))
            for col in df.columns:
                display(HTML(f'<b>{col}:</b>'))
                display(HTML(f'{df[col].values}'))
        
        display(HTML(f"<h2>MANUAL TESTS</h2>"))
        for w in self.widgets:
            display(w)
        display(HTML(f"<h2>ADDITIONAL FEEDBACK</h2>"))
        display(self.feedback)
        
    def values(self):
        values = {'values':[w.description for w in self.widgets if w.value],
                  'feedback':self.feedback.value}
        return values

    def save_values(self):
        pd.Series(data=self.values().get('values'), 
        name='options').to_csv(f'grades/nbta_selection_{self.question_name}.csv', index=False)

        with open(f'grades/nbta_feedback_{self.question_name}.txt', 'w') as f:
                f.write(self.values().get('feedback'))
        print(f'Saved options and feedback for {self.question_name}')



class EstimatedMark:
    def __init__(self, question_name='estimated_mark', options=None, auto_tests=None):
        self.base_dir = '../..'
        self.question_name = question_name
        self.grade_selector = self.set_grade_selector()
        self.display()
    
    def set_grade_selector(self):
        try:
            self.selected_option = pd.read_csv(f'grades/nbta_selection_{self.question_name}.csv')['options'].values.astype(str)
        except:
            self.selected_option = '2.1'

        est_grade = widgets.RadioButtons(
            options=['High 1st', '1st', '2.1', '2.2', '3rd', 'fail'],
            value=self.selected_option,
            description='Assessed score:',
            disabled=False)

        return est_grade
    
    def display(self):
        display(HTML(f"<h2>ESTIMATED MARK</h2>"))
        display(self.grade_selector)
        
    def save_values(self):
        pd.Series(data=[self.grade_selector.value], 
        name='options').to_csv(f'grades/nbta_selection_{self.question_name}.csv', index=False)
        print(f'Saved {self.question_name}')


class GradingSchema():
    def __init__(self,name,total_points,add_tests=None):
        self.name = name
        self.total_points = total_points
        self.add_tests = add_tests
        self.markings = None
        self.style = None
        self.grades = None

    def load_marks(self, folder, candidates):
        question_cols = pd.read_csv(f'grading/testing/notebook_tests/{self.name}.csv').options.values
        cols = ['candidate','additional_comments']+list(question_cols)
        marking = pd.DataFrame(data=[], columns=cols)

        for candidate in tqdm(candidates):
            init_values = [candidate,''] + [np.nan for _ in question_cols]
            marking.loc[marking.shape[0]+1] = init_values

            try:
                base_dir = f'{folder}/{candidate}/grades'
                values = pd.read_csv(f'{base_dir}/nbta_selection_{self.name}.csv')['options'].values
                with open(f'{base_dir}/nbta_feedback_{self.name}.txt') as f:
                    text = f.readlines()
                marking.loc[marking.shape[0],'additional_comments'] = "\n".join(text)
                marking.loc[marking.shape[0],question_cols] = False
                marking.loc[marking.shape[0],values] = True
                self.style = pd.read_csv(f'{base_dir}/nbta_selection_style.csv')['options'].values
                self.estimated_grade = pd.read_csv(f'{base_dir}/nbta_selection_estimated_grade.csv')['options'].values
            except Exception as e:
                print(f'Failed on candidate {candidate}: {e}')
        
        for bool_question in question_cols:
            marking.loc[:,bool_question] = marking.loc[:,bool_question].astype(bool)

        if self.add_tests is not None:
            for test in self.add_tests:
                test_results = pd.read_csv(f'grading/scores/{test}.csv')
                marking = marking.merge(test_results, on='candidate', how='outer')
        
        self.markings = marking.copy()
        return self

    def simple_grading(self, df):
        marks = pd.Series(name='marks', data=np.zeros(df.shape[0]))
        max_points = 0
        for col in df.columns.values:
            if df[col].dtype == bool:
                if (col.split('_')[0] == 'neg') or (col == 'not_answered'):
                    marks = marks + np.abs(df[col]-1)
                else:
                    marks = marks + df[col]
                max_points += 1
        mask = np.abs(df.not_answered-1)
        marks = marks.apply(lambda x: 0 if x<0 else x)
        marks = marks*mask
        final_mark = marks/max_points*self.total_points
        print(f'Max points: {max_points}, Total mark:{self.total_points}, Mean mark±1SD:{np.mean(final_mark)}±{np.std(final_mark)}')
        return final_mark


    def grade(self):
        self.grades = self.simple_grading(self.markings).copy()
        return self.grades



class Grader():
    def __init__(self, marker, schemas):
        self.marker = marker
        self.style_schema = GradingSchema('style',100)
        self.schemas = dict(zip([s.name for s in schemas],schemas))
        self.grades = pd.DataFrame()
        self.grades['candidate'] = self.marker.candidates
        self.folder = self.marker.base_dir

    def grade(self, questions=None):
        if questions is None:
            questions = self.schemas.keys()
        elif not questions.isinstance(list):
            questions = [questions]
        
        self.grades['total'] = 0
        for question in questions:
            print(f"Grading question {question}")
            schema = self.schemas.get(question)
            schema.load_marks(self.folder, self.grades['candidate'].values)
            self.grades[schema.name] = schema.grade()
            self.grades['total'] = self.grades['total'] + self.grades[schema.name]
        
        print(f"Grading coding style")
        self.style_schema.load_marks(self.folder, self.grades['candidate'].values)
        self.grades['coding_style'] = self.style_schema.grade()

        print(f"Gathering estimated marks")
        est_marks = []
        for candidate in tqdm(self.grades['candidate'].values):
            mark = pd.read_csv(f'{self.folder}/{candidate}/grades/nbta_selection_estimated_grade.csv')
            est_marks.append(mark.loc[0,'options'])
        self.grades['estimated_marks'] = est_marks
        return self

    def marking_for_question(self, question):
        return self.schemas.get(question).markings

    def grading_for_question(self, question):
        return self.schemas.get(question).grades

