import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
import numpy as np
import pandas as pd
import sys
import os
from os import path
from nbta.utils import header_cell, header_code_cell
from tqdm import tqdm


class ParsedNotebook():
    '''
    Usage: ParsedNotebook(path, questions)

    A parsed Jupyter notebook and associated questions
    '''

    def __init__(self, path, author, file_name):
        with open(path, 'r') as f:
            self.content = nbf.read(f, as_version=nbf.NO_CONVERT)
        base_dir = '/'.join(path.split('/')[:-1])
        self.file_name = f'{base_dir}/{file_name}'
        self.author = author
        self.modified_content = None

    def insert_cells(self, new_cells):
        cells = self.content['cells']
        self.modified_content = self.content.copy()
        modified_cells = [header_cell(self.author), header_code_cell(self.author)]

        for this_cell in cells:
            inserted = False
            for new_cell in new_cells:
                if  new_cell.tag in this_cell['source']:
                    if new_cell.position == 'before':
                        modified_cells.append(new_cell.cell)
                        modified_cells.append(this_cell)
                    else: 
                        modified_cells.append(this_cell)
                        modified_cells.append(new_cell.cell)
                    inserted = True
            if not inserted:
                modified_cells.append(this_cell)

        tests_list = [f'nbta_test_{c.name}' for c in new_cells]
        final_cell_text = ','.join(tests_list)
        final_cell_code = f'[t.save_values() for t in [{final_cell_text}]]'
        modified_cells.append(nbf.v4.new_code_cell(source=final_cell_code))

        self.modified_content['cells'] = modified_cells

        return self

    def execute_notebook(self, kernel):
        ep = ExecutePreprocessor(timeout=99999999,kernel_name=kernel)
        ep.preprocess(self.modified_content)

        return None

    def write(self):
        if self.modified_content is None:
            content = self.content
        else:
            content = self.modified_content

        with open(f'{self.file_name}.ipynb', 'w') as f:
            nbf.write(content,f)

class MarkingCell():
    def __init__(self, name, tag, cell_type='code', position='before', from_file=True, source_data=None):
        if from_file is False and source_data is None:
            raise Exception("Either from_file must be True or source_data must not be a NoneType")

        if from_file is True:
            self.check_source_dir()
            source_path = f"grading/testing/notebook-tests/{name}.py"
            if not os.path.exists(source_path):
                self.create_test_file(source_path)
            
            options_path = f"grading/testing/notebook-tests/{name}.csv"
            if not os.path.exists(options_path):
                self.initialise_options(options_path)

            with open(source_path, 'r') as f:
                source = ''.join(f.readlines())

        if cell_type == 'code':
            self.cell = nbf.v4.new_code_cell(source=source)
        elif cell_type == 'markdown':
            self.cell = nbf.v4.new_markdown_cell(source=source)
        else:
            raise Exception(f"Unknown cell type: {cell_type}")
        self.tag = tag
        self.position = position
        self.name = name

    def check_source_dir(self):
        grading_dirs = ["grading", "grading/testing","grading/testing/notebook-tests",
        "grading/scores", "grading/testing/external-tests"]

        for path in grading_dirs:
            if not os.path.isdir(path):
                os.mkdir(path)

    def create_test_file(self, path):
        test_name = path.split("/")[-1].strip(".py")
        code = [f"# TEST FOR QUESTION {test_name}",
        "from nbta.grading import QuestionGrader",
        f"nbta_test_{test_name} = QuestionGrader('{test_name}')"]
        code = "\n".join(code)

        with open(path, 'w') as f:
                f.write(code)

    def initialise_options(self, path):
        options = "\n".join(["options,feedback","not_answered,you have not answered the question", 
        "failed, you have not understood this question", "pass, you understood the basics of this question; However more could have been done.", 
        "high_pass, you understood the basics of this question", "merit, you understood the question well","high_merit, you answered the question very well", "distinction, your answer is in the top 10% of the class", "high_distinction, your answer is in the top 5% of the class"])
        with open(path, 'w') as f:
                f.write(options)
 

class NotebookMarker():
    def __init__(self, folder, notebook_name, name_func=None, kernel='python3'):
        self.notebook_name = notebook_name
        self.kernel = kernel
        self.name_func = name_func
        self.base_dir = folder
        self.marking_name = f'{self.notebook_name}_marking'
        self.candidates = self.filter_dirs(os.listdir(self.base_dir))
        self.notebooks = self.get_notebooks()
        self.test_list = None

    def filter_dirs(self, candidates):
        if '.DS_Store' in candidates:
            candidates.remove('.DS_Store')
        if '.ipynb_checkpoints' in candidates:
            candidates.remove('.ipynb_checkpoints')
        return candidates

    def insert_cells(self, cells_data):
        for auth, notebook in self.notebooks.items():
            notebook.insert_cells(cells_data).write()
        return self

    def get_notebooks(self):
        notebooks = {}
        for candidate in self.candidates:
            try:
                path = f'{self.base_dir}/{candidate}/{self.notebook_name}.ipynb'
                notebook = ParsedNotebook(path, candidate, self.marking_name)
                notebooks[candidate] = notebook
            except Exception as e:
                pass
        return notebooks

    def register_autotest(self):
        test_list = os.listdir("grading/testing/external-tests")
        test_list = [name.split('.')[0] for name in test_list if name.endswith(".py")]
        return test_list

    def run_autotests(self):
        test_results = {}
        for the_test in self.register_autotest():
            print(f"Now running test {the_test}")
            test_results[the_test]= self.run_single_test(the_test)
            test_results[the_test].to_csv(f'grading/scores/{the_test}.csv')

        self.test_results = test_results
        
        return self.test_results

    def run_single_test(self, the_test):
        results = None
        absolute_path = os.getcwd()
        sys.path.insert(0, f'{absolute_path}/grading/testing/external-tests')
        
        for candidate in tqdm(self.candidates):
            mod = __import__(the_test, fromlist=[the_test])
            tester = getattr(mod, the_test)
            result = tester(folder=f'{self.base_dir}/{candidate}').run_test()

            if results is None:
                results = pd.DataFrame(data=[result.values()],columns=result.keys())
                results['candidate'] = candidate
            else:
                formatted_result = pd.DataFrame(data=[result.values()],columns=result.keys())
                formatted_result['candidate'] = candidate
                results = pd.concat([results,formatted_result])
        
        return results.reset_index(drop=True)



    def run_notebooks(self):
        for auth, notebook in self.notebooks.items():
            print(f'Running notebook for {auth}')
            notebook.execute_notebook(kernel=self.kernel)
        return self
    
if __name__ == '__main__':
    with open('code_cells/final_cell.py') as f:
            lines = f.readlines()
    print(lines)
