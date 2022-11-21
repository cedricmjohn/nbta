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
    def __init__(self, question_name, options=None, auto_tests=None, feedback=False):
        self.base_dir = '../..'
        self.question_name = question_name
        self.auto_tests=auto_tests
        self.auto_tests_results={}
        self.feedback = feedback

        if not os.path.exists('grades'):
                os.mkdir('grades')

        if self.auto_tests is not None:
            self.run_autotests()

        if self.feedback:
            try:
                self.selected_pos_feedback = pd.read_csv(f'grades/nbta_pos_feedback_{self.question_name}.txt')
            except:
                self.selected_pos_feedback = None
            
            try:
                self.selected_neg_feedback = pd.read_csv(f'grades/nbta_neg_feedback_{self.question_name}.txt')
            except:
                self.selected_neg_feedback = None
            
            self.feedback = self.set_feedback()
        else:
            try:
                self.selected_values = pd.read_csv(f'grades/nbta_selection_{self.question_name}.csv')['options'].values
            except:
                self.selected_values = None
        
            if options is None:
                self.options = self.read_options(f'{self.base_dir}/grading/testing/notebook_tests/{self.question_name}.csv')
            else:
                self.options = options
        
            self.autoresults = self.set_autoresults_widget()
            self.widgets = self.set_widgets()

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
        feedbacks = []
        if self.selected_pos_feedback is not None:
            with open(f'grades/nbta_pos_feedback_{self.question_name}.txt', 'r') as f:
                pos_feedback_text = '\n'.join(f.readlines())
        else:
            pos_feedback_text = ' '
        
        if self.selected_neg_feedback is not None:
            with open(f'grades/nbta_neg_feedback_{self.question_name}.txt', 'r') as f:
                neg_feedback_text = '\n'.join(f.readlines())
        else:
            neg_feedback_text = ' '

        feedbacks.append(widgets.Textarea(
            value=pos_feedback_text,
            placeholder=pos_feedback_text,
            description='POSITIVES:',
            disabled=False))

        feedbacks.append(widgets.Textarea(
            value=neg_feedback_text,
            placeholder=neg_feedback_text,
            description='NEGATIVES:',
            disabled=False))
        
        return feedbacks
    
    def display(self):
        if self.feedback:
            display(HTML(f'<h1 style="color:blue">{self.question_name.replace("_"," ")}</h1>'))
            display(HTML(f'<h4 style="color:red">Remember to be positive and constructive in your feedbacks!</h4>'))
            display(HTML(f'<p>Students are very sensitive to feedback, and will react to unfair statements. The goal is to provide useful information that will help students improve. When you write negative feedback, frame them as things that can be improved, and try to explain how. Balance the positive and the negative feedbacks, and give about 3-4 each positive & negative feedbacks per question. <br>Remember that your text will be added to more feedback from the automatic and manual tests, and is addressed to the student (so you can use "you").</p>'))
            for feedback in self.feedback:
                display(feedback)
        else:
            display(HTML(f'<h1 style="color:blue">{self.question_name.replace("_"," ")}</h1>'))

            if len(self.auto_tests_results.items()) > 0:
                display(HTML(f'<h2 style="color:teal">AUTOMATIC TESTS</h2>'))
            for test,df in self.auto_tests_results.items():
                display(HTML(f'<h3 style="color:purple">{test.upper()}</h3>'))
                for col in df.columns:
                    display(HTML(f'<b>{col}:</b>'))
                    display(HTML(f'{df[col].values}'))
        
            display(HTML(f'<h2 style="color:teal">MANUAL CHECKS</h2>'))
            for w in self.widgets:
                display(w)

        
    def values(self):
        values = {'values':[w.description for w in self.widgets if w.value]}
        return values

    def save_values(self):
        if self.feedback:
            with open(f'grades/nbta_pos_feedback_{self.question_name}.txt', 'w') as f:
                f.write(self.feedback[0].value)
            with open(f'grades/nbta_neg_feedback_{self.question_name}.txt', 'w') as f:
                f.write(self.feedback[1].value)
            print(f'Saved feedbacks for {self.question_name}')
        else:
            pd.Series(data=self.values().get('values'),
            dtype=object, 
            name='options').to_csv(f'grades/nbta_selection_{self.question_name}.csv', index=False)
            print(f'Saved options for {self.question_name}')



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
    def __init__(self,name,total_points,add_tests=None, ignore_feedbacks=[]):
        self.name = name
        self.total_points = total_points
        self.add_tests = add_tests
        self.markings = None
        self.style = None
        self.grades = None
        self.ignore_feedbacks = ignore_feedbacks

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

    def build_feedback(self, values, all_feedbacks):
        if values['not_answered'] == 1:
            return f'You did not answer {self.name}.'

        neg_feedbacks = []
        pos_feedbacks = []
        for f in all_feedbacks:
            if values[f] == 0:
                neg_feedbacks.append(f)
            else:
                pos_feedbacks.append(f)
        feedback_string = ''
        pos_feedback_string = ''
        neg_feedback_string = ''
        if len(pos_feedbacks)>0:
            pos_feedback_string = f'You did the following well in {self.name}:\n'
            pos_items = '\n'.join([f'    • {self.feedback_dict.get(f)}' for f in pos_feedbacks])
            pos_feedback_string = f'{pos_feedback_string}{pos_items}\n'
        if len(neg_feedbacks)>0:
            neg_feedback_string = f'Improvements in {self.name} would be possible for the following (either your did not do that, or not to the highest standard):\n'
            neg_items = '\n'.join([f'    • {self.feedback_dict.get(f)}' for f in neg_feedbacks])
            neg_feedback_string = f'{neg_feedback_string}{neg_items}\n'
        add_feedback = ''
        if values['additional_comments'] not in ['', ' ']:
            add_feedback = f'Additional feedback for this question: {values["additional_comments"]}\n\n'

        feedback_string = f'{pos_feedback_string}\n{neg_feedback_string}\n{add_feedback}'

        return feedback_string

    def get_feedback(self):
        feedback_options = pd.read_csv(f'grading/testing/notebook_tests/{self.name}.csv')
        self.feedback_dict = dict(zip(feedback_options.options.values,feedback_options.feedback.values))
        feedbacks = pd.DataFrame()
        feedbacks['candidate'] = self.markings.candidate
        feedbacks['feedback'] = '\n'

        ignore = self.ignore_feedbacks+['candidate', 'additional_comments','not_answered']

        cols = [c for c in self.markings.columns.values if c not in ignore]

        neg_feedbacks = [f for f in cols if f.split('_')[0] == 'neg']
        pos_feedbacks = [f for f in cols if f not in neg_feedbacks]

        values = self.markings.copy()
        values[neg_feedbacks] = abs(values[neg_feedbacks]-1)

        all_feedbacks = neg_feedbacks + pos_feedbacks

        print(f"Generating feedback for {self.name}:")
        for index, row in tqdm(values.iterrows()):
            feedbacks.loc[index,'feedback'] = f'{self.build_feedback(row,all_feedbacks)}'

        self.feedbacks = feedbacks

        return feedbacks

    def simple_grading(self, df):
        marks = pd.Series(name='marks', data=np.zeros(df.shape[0]))
        max_points = 0
        for col in df.columns.values:
            if df[col].dtype == bool:
                if (col.split('_')[0] == 'neg') or (col == 'not_answered'):
                    marks = marks + np.abs(df[col].values-1)
                else:
                    marks = marks + df[col].values
                max_points += 1
        mask = np.abs(df.not_answered-1)
        marks = marks.apply(lambda x: 0 if x<0 else x)
        marks = marks.values*mask
        self.max_points = max_points
        final_mark = marks/max_points*self.total_points
        print(f'Max points: {max_points}, Total mark:{self.total_points}, Mean mark±1SD:{np.mean(final_mark)}±{np.std(final_mark)}')
        return final_mark


    def calculate_grades(self):
        grades = self.simple_grading(self.markings)
        return grades
    
    def grade(self):
        grade_per_candidate = pd.DataFrame()
        grade_per_candidate['candidate'] = self.markings.candidate
        grade_per_candidate[self.name] = self.calculate_grades()
        self.grades = grade_per_candidate
        return self.grades



class Grader():
    def __init__(self, marker, schemas):
        self.marker = marker
        self.reset_grades()
        self.style_schema = GradingSchema('style',100)
        self.schemas = dict(zip([s.name for s in schemas],schemas))
        self.folder = self.marker.base_dir

    def make_feedback(self, pre='', post=''):
        self.grades['feedback'] = self.grades['candidate'].apply(lambda x: f'{pre}\n')
        
        for q in tqdm(self.schemas.keys()):
            current_feedback = self.grades[['candidate','feedback']].copy()
            current_feedback = current_feedback.merge(self.schemas.get(q).get_feedback(), on='candidate')
            current_feedback['feedback'] = current_feedback['feedback_x'] + current_feedback['feedback_y']
            self.grades['feedback'] = current_feedback['feedback'].copy()


        self.grades['feedback'] = self.grades['feedback'].apply(lambda x: f'{x}{post}')

        return self

    def reset_grades(self):
        self.grades = pd.DataFrame()
        self.grades['candidate'] = self.marker.candidates

    def grade(self, questions=None):
        self.reset_grades()

        if questions is None:
            questions = self.schemas.keys()
        elif not questions.isinstance(list):
            questions = [questions]
        
        self.grades['total'] = 0
        for question in questions:
            print(f"Grading question {question}")
            schema = self.schemas.get(question)
            schema.load_marks(self.folder, self.grades['candidate'].values)
            self.grades = self.grades.merge(schema.grade(), on = 'candidate')
            self.grades['total'] = self.grades['total'] + self.grades[schema.name]
        self.grades['total'] = np.round(self.grades['total'],0)

        print(f"Grading coding style")
        self.style_schema.load_marks(self.folder, self.grades['candidate'].values)
        style_results = self.style_schema.grade()
        style_results.columns = ['candidate','coding_style']
        self.grades = self.grades.merge(style_results, on = 'candidate')
        
        print(f"Gathering estimated marks")
        est_marks = pd.DataFrame()
        est_marks['candidate'] = self.grades['candidate']
        est_marks['estimated_marks']=np.nan
        for candidate in tqdm(self.grades['candidate'].values):
            mark = pd.read_csv(f'{self.folder}/{candidate}/grades/nbta_selection_estimated_grade.csv')
            est_marks.loc[est_marks.candidate==candidate,'estimated_marks']=mark.loc[0,'options']
        self.grades = self.grades.merge(est_marks, on = 'candidate')
        return self

    def marking_for_question(self, question):
        return self.schemas.get(question).markings

    def grading_for_question(self, question):
        return self.schemas.get(question).grades

