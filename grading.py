import pandas as pd
import ipywidgets as widgets
from IPython.display import display

class NBTATest:
    def __init__(self,folder,*kwargs):
        self.results = kwargs
        self.folder = folder
        self.test_results = None

    def run_test(self):
        pass

    def get_results(self):
        return self.test_results

class QuestionGrader:
    def __init__(self, test_name, options=None, auto_tests=None):
        self.base_dir = '../..'
        self.test_name = test_name
        self.auto_tests=auto_tests
        
        try:
            self.selected_values = pd.read_csv(f'nbta_points_{self.test_name}.csv')['options'].values
        except:
            self.selected_values = None
            
        try:
            self.selected_feedback = pd.read_csv(f'nbta_feedback_{self.test_name}.txt')
        except:
            self.selected_feedback = None
        
        if options is None:
            self.options = self.read_options(f'{self.base_dir}/tests/options/{self.test_name}.csv')
        else:
            self.options = options
        
        self.widgets = self.set_widgets()
        self.feedback = self.set_feedback()
        self.display()
            
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
    
    def set_feedback(self):
        if self.selected_feedback is not None:
            with open(f'nbta_feedback_{self.test_name}.txt', 'r') as f:
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
        for w in self.widgets:
            display(w)
        display(self.feedback)
        
    def values(self):
        values = {'values':[w.description for w in self.widgets if w.value],
                  'feedback':self.feedback.value}
        return values

    def save_values(self):
        pd.Series(data=self.values().get('values'), 
        name='options').to_csv(f'nbta_points_{self.test_name}.csv', index=False)

        with open(f'nbta_feedback_{self.test_name}.txt', 'w') as f:
                f.write(self.values().get('feedback'))

        return self