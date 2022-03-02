import nbformat as nbf
import numpy as np
import pandas as pd
import os

class ParsedNotebook():
    def __init__(self, path, questions):
        with open(path, 'r') as f:
            self.content = nbf.read(f, as_version=nbf.NO_CONVERT)
        self.questions = questions
        self.index = self.parse_questions(self.questions)

    def parse_questions(self, questions):
        
        questions_indexes = {}
        cells = self.content['cells']

        for this_cell in cells:
            for question in questions.keys():
                if  questions[question] in this_cell['source']:
                    questions_indexes[question] = cells.index(this_cell)
        
        return questions_indexes
    
    def yield_cells(self,from_cell, to_cell):
        return self.content['cells'][from_cell:to_cell]



class NotebookMarker():
    def __init__(self, folder_path, questions):
        self.base_dir = folder_path
        self.questions = questions
        candidates = os.listdir(self.base_dir)
        if '.DS_Store' in candidates:
            candidates.remove('.DS_Store')
        if '.ipynb_checkpoints' in candidates:
            candidates.remove('.ipynb_checkpoints')
        self.candidates = candidates
        self.notebooks = self.get_notebooks()

    def get_notebooks(self):
        notebooks = {}
        for candidate in self.candidates:
            try:
                path = f'{self.base_dir}/{candidate}/01-Assessment-Python-Data-Preparation.ipynb'
                notebook = ParsedNotebook(path, self.questions)
                notebooks[candidate] = notebook
            except Exception as e:
                pass
        return notebooks

    def generate_question_notebooks(self):
        questions = [q for q in list(self.questions.keys()) if 'Q' in q]
        offset = list(self.questions.keys()).index(questions[0])

        for q_index, question in enumerate(questions):
            nb = nbf.v4.new_notebook()
            cells = []
            cells.append(nbf.v4.new_code_cell(source=f'''
            import pandas as pd
            import numpy as np
            candidates = []; marks = []; feedbacks=[]
            style_contrib=0.3
            '''))

            for author,notebook in self.notebooks.items():
                cells.append(nbf.v4.new_markdown_cell(source=f'# MARKING-{question}-{author}'))
                cells.append(nbf.v4.new_code_cell(source=f'name="{author}"'))
                try:
                    from_cell = notebook.index[question]
                    to_cell = notebook.index[list(self.questions.keys())[q_index+offset+1]]
                    cells = cells + notebook.yield_cells(from_cell, to_cell)
                    cells.append(nbf.v4.new_code_cell(source=f'# Run test for marking'))
                    cells.append(nbf.v4.new_code_cell(f'raw_mark='))
                    cells.append(nbf.v4.new_code_cell(source='style=0.5'))
                    cells.append(nbf.v4.new_code_cell(f'mark=raw_mark*(1-style_contrib)+raw_mark*style_contrib*style'))
                    cells.append(nbf.v4.new_code_cell(source=f'feedback="""Feeback on {question}: Good answer, no issues"""'))
                except: 
                    cells.append(nbf.v4.new_code_cell(source='mark=0'))
                    cells.append(nbf.v4.new_code_cell(source='style=0'))
                    cells.append(nbf.v4.new_code_cell(source=f'feedback="""Feeback on {question}: Not answered"""'))
                cells.append(nbf.v4.new_code_cell(source=f'candidates.append(name); marks.append(mark); feedbacks.append(feedback)'))

            cells.append(nbf.v4.new_code_cell(source=''' 
            df_dict = {"candidates":candidates, "Mark":marks, "Feedback":feedbacks}
            df = pd.DataFrame.from_dict(df_dict)
            df.to_csv("marks_Q1.csv", index=False)
            df.head(10)
            '''))
            cells.append(nbf.v4.new_code_cell(source='df.Mark.hist()'))
            nb['cells'] = cells
            with open(f'Question_{question}.ipynb', 'w') as f:
                nbf.write(nb,f)

    def write_specific_notebook(self,author):
        with open(f'{author}.ipynb', 'w') as f:
            nbf.write(self.notebooks[author].content,f)


if __name__ == '__main__':
    questions = {
            'Setup':"# INITIAL SETUP",
            'Part_A_Dataload':"#import pickle",
            'Q1': "## Question 1 [3 marks]",
            'Q2': "## Question 2 [3 marks]",
            'Q3': "## Question 3 [8 marks]",
            'Q4': "## Question 4 [6 marks]",
            'Q5': "## Question 5 [10 marks]",
            'Q6': "## Question 6 [10 marks]",
            'Q7': "## Question 7 [10 points]",
            'Q8': "## Question 8 [10 points]",
            'Q9': "## Question 9 [15 points]",
            'Q10': "## Question 10 [25 points]",
            'final_cell': "# 🚨 CHECK AND SAVE YOUR ANSWERS BEFORE PUSHING 🚨",
        }
    marker = NotebookMarker('late_submissions', questions)
    marker.generate_question_notebooks()
    #marker.write_specific_notebook('akmalbasri26')
