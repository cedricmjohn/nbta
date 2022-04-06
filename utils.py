from datetime import datetime
import nbformat as nbf 
import os

def header_cell(author):
    # datetime object containing current date and time
    now = datetime.now()
    dt_string = now.strftime("on %d/%m/%Y at %H:%M:%S")

    source = [f'# MARKING NOTEBOOK [{author}]',
    f'### Generated {dt_string}']
    source = '\n'.join(source)
    return nbf.v4.new_markdown_cell(source=source)

def header_code_cell(author):
    absolute_path = os.getcwd()

    source = ['%load_ext autoreload',
    '%autoreload 2',
    '',
    'import numpy as np',
    'import pandas as pd',
    'import matplotlib.pyplot as plt',
    'from nbta.grading import QuestionGrader, EstimatedMark',
    'import sys'
    '',
    '# Adding local test classes to the Python path:',
    f'sys.path.insert(0, f"{absolute_path}/grading/testing/notebook_tests")',
    f'sys.path.insert(1, f"{absolute_path}/grading/testing/external_tests")'
    ]
    
    source = '\n'.join(source)

    return nbf.v4.new_code_cell(source=source)
    
def footer_cell():
    lines = [f"nbta_test_style = QuestionGrader('style')",
    "nbta_estimated_mark = EstimatedMark()"]
    return "\n".join(lines)



class NotAssigned():
    def __init__(self,expected_type=''):
        self.expected_type = expected_type
        return None