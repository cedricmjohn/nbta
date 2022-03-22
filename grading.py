import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import os
import sys

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
            self.selected_values = pd.read_csv(f'nbta_score_{self.question_name}.csv')['options'].values
        except:
            self.selected_values = None
            
        try:
            self.selected_feedback = pd.read_csv(f'nbta_feedback_{self.question_name}.txt')
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
        name='options').to_csv(f'grades/nbta_points_{self.question_name}.csv', index=False)

        with open(f'grades/nbta_feedback_{self.question_name}.txt', 'w') as f:
                f.write(self.values().get('feedback'))
        print(f'Saved options and feedback for {self.question_name}')