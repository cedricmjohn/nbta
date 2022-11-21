import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError
import pandas as pd
import sys
import os
from os import path
import shutil
from nbta.utils import footer_cell, header_cell, header_code_cell
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
        modified_cells = header_cell(self.author) + [header_code_cell(self.author)]

        for this_cell in cells:
            inserted = False
            cells_before = []
            cells_after = []
            begin_marking = '<span style="color:darkred">==============================================================MARK THIS QUESTION BELOW=================================================================</span>\n<h1 style="color:darkred">YOUR MARKS</h1>'
            for new_cell in new_cells:
                if  new_cell.tag in this_cell['source']:
                    if new_cell.position == 'before':
                        if len(cells_before)==0:
                            cells_before.append(nbf.v4.new_markdown_cell(source=begin_marking))
                        cells_before.append(new_cell.cell)
                    else:
                        if len(cells_after)==0:
                            cells_after.append(nbf.v4.new_markdown_cell(source=begin_marking)) 
                        cells_after.append(new_cell.cell)
                    inserted = True
            if inserted:
                cells_before.append(this_cell)
                modified_cells = modified_cells + cells_before + cells_after
            else:
                modified_cells.append(this_cell)

        modified_cells.append(nbf.v4.new_markdown_cell(source='<h1 style="color:blue">Coding style and private feedback to lecturer</h1>"'))
        modified_cells.append(nbf.v4.new_code_cell(source=footer_cell()))
        tests_list = [f'nbta_test_{c.name}' for c in new_cells]
        tests_list=tests_list+['nbta_test_style','nbta_estimated_mark','nbta_private_feedback']
        title_cell_text = '<h1 style="color:red">RUN the cell below to save your markings</h1>"'
        modified_cells.append(nbf.v4.new_markdown_cell(source=title_cell_text))
        final_cell_text = ','.join(tests_list)
        final_cell_code = ['# DONT FORGET TO SAVE:','',f'import os','',
        f'all_tests = [{final_cell_text}]','',
        f'for t in all_tests:',
        f'    t.save_values()','',
        f'print("Saved First Marker as:", os.getlogin())'
        f'pd.Series(data=[os.getlogin()], name="marker_name").to_csv("grades/first_marker.csv", index=False)']
        final_cell_code = '\n'.join(final_cell_code)
        modified_cells.append(nbf.v4.new_code_cell(source=final_cell_code))

        self.modified_content['cells'] = modified_cells

        return self

    def yield_question_cells(self,start_question,end_question):
        return_cells = [nbf.v4.new_markdown_cell(source=f'ANSWER FROM: {self.author}')]
        in_scope = False
        for this_cell in self.content['cells']:
            if start_question.tags in this_cell['source']:
                in_scope = True
                return_cells.append(this_cell)
            if end_question is not None:
                if end_question.tags in this_cell['source']:
                    in_scope = False
                    return return_cells
            if in_scope:
                return_cells.append(this_cell)
        return return_cells

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
            source_path = f"grading/testing/notebook_tests/{name}.py"
            if not os.path.exists(source_path):
                self.create_test_file(source_path)
            
            with open(source_path, 'r') as f:
                source = ''.join(f.readlines())
            
            options_path = f"grading/testing/notebook_tests/{name}.csv"
            if not os.path.exists(options_path):
                self.initialise_options(options_path)
            
            style_path = f"grading/testing/notebook_tests/style.csv"
            if not os.path.exists(style_path):
                self.initialise_styles(style_path)

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
        grading_dirs = ["grading", "grading/testing","grading/testing/notebook_tests",
        "grading/scores","grading/scores/individual", "grading/testing/external_tests"]

        for path in grading_dirs:
            if not os.path.isdir(path):
                os.mkdir(path)

    def create_test_file(self, path):
        test_name = path.split("/")[-1].strip(".py")
        code = [f"# TEST FOR QUESTION {test_name}",
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

    def initialise_styles(self, path):
        options = "\n".join(["options,feedback",
        "good use of functions","logical variable names","pythonic style","good use of markdown",
        "appropriate level of comments", "good use of graphs", "some graphs", "no graphs",
        "best solution", "simple solution", "complicated solution", "overly complicated solution"])
        with open(path, 'w') as f:
                f.write(options)
 
class FeedbackCell:
    def __init__(self, tag, name="STUDENT_FEEDBACK",position='before'):
        self.name = name
        self.tag = tag
        self.position = position

        source = f"nbta_test_{self.name} = QuestionGrader('{self.name}', feedback=True)"
        self.cell = nbf.v4.new_code_cell(source=source)
        return None

class NotebookMarker():
    def __init__(self, folder, notebook_name, questions=None,name_func=None):
        self.notebook_name = notebook_name
        self.name_func = name_func
        self.base_dir = folder
        self.marking_name = f'{self.notebook_name}_marking'
        self.questions = questions
        self.candidates = self.filter_dirs(os.listdir(self.base_dir))
        self.notebooks = self.get_notebooks()
        self.test_list = None

    def filter_dirs(self, candidates):
        if '.DS_Store' in candidates:
            candidates.remove('.DS_Store')
        if '.ipynb_checkpoints' in candidates:
            candidates.remove('.ipynb_checkpoints')
        return candidates

    def insert_cells(self, cells_data=None):
        if cells_data is None:
            if self.questions is None:
                return self
            cells_data = self.questions

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
                print(f'Error on candidate {candidate}:{e}')
        return notebooks

    def register_autotest(self):
        test_list = os.listdir("grading/testing/external_tests")
        test_list = [name.split('.')[0] for name in test_list if name.endswith(".py")]
        return test_list

    def run_autotests(self):
        test_results = {}
        sys.path.insert(0, f'{os.getcwd()}/grading/testing/external_tests')
        sys.path.insert(1, f'{os.getcwd()}/grading/testing/notebook_tests')
        for the_test in self.register_autotest():
            print(f"Now running test {the_test}")
            test_results[the_test]= self.run_single_test(the_test)
            test_results[the_test].to_csv(f'grading/scores/{the_test}.csv')

        self.test_results = test_results
        
        return self.test_results

    def run_single_test(self, the_test):
        results = None
        
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



    def run_notebooks(self,save_originals=None, kernel='python3', first_run=True):

        if first_run:
            try:
                results = pd.read_csv('grading/scores/nbta_runs.csv')
            except:
                results = pd.DataFrame(data=[], columns=['candidate','status','message'])

        ep = ExecutePreprocessor(kernel_name=kernel,
        allow_errors=True)

        for auth, notebook in tqdm(self.notebooks.items()):

            if (first_run and auth not in results.candidate.values) or (not first_run):
                passed,auth_errors = self.run_single_notebook(auth, notebook.modified_content.copy(),save_originals,ep)
                row = {'candidate': auth, 'status': passed, 'message': auth_errors}
                results = results.append(row, ignore_index = True)
                results.to_csv('grading/scores/nbta_runs.csv', index=False)
            
        self.runs_results = pd.read_csv('grading/scores/nbta_runs.csv')

        return self

    def run_single_notebook(self, auth, nb, save_originals, ep):
        super_path = os.getcwd()
        if save_originals is not None:
            for original_file in save_originals:
                try:
                    shutil.copy(f'{self.base_dir}/{auth}/{original_file}', f'{self.base_dir}/{auth}/nbta_{original_file}')
                except:
                    pass
        os.chdir(f'{super_path}/{self.base_dir}/{auth}')
        notebook_filename_out = f'{self.notebook_name}_marking.ipynb'

        try:
            out = ep.preprocess(nb, {'metadata': {'path': ''}})
        except CellExecutionError as e:
            print(e)
        finally:
            with open(notebook_filename_out, mode='w', encoding='utf-8') as f:
                nbf.write(nb, f)
        auth_errors = []
        passed = True
        for cell in nb['cells']:
            if cell['cell_type']=='code':
                for output in cell['outputs']:
                    if output['output_type'] == 'error':
                        auth_errors.append(f"{output['ename']}: {output['evalue']}")
                        passed = False

        os.chdir(super_path)
        return passed, auth_errors

    def generate_question_notebooks(self):
        questions = self.questions
        for index,question in enumerate(questions):
            if index+1 != len(questions):
                next_question = questions[index+1]
            else:
                next_question = None

            cells = []
            for auth, notebook in self.notebooks.items():
                cells = cells + notebook.yield_question_cells(question,next_question)
                  
            question_notebook = nbf.v4.new_notebook()    
            question_notebook['cells'] = cells

            with open(f'{question.name}_all_answers.ipynb', 'w') as f:
                nbf.write(question_notebook,f)



if __name__ == '__main__':
    with open('code_cells/final_cell.py') as f:
            lines = f.readlines()
    print(lines)
