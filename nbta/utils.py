from datetime import datetime
import nbformat as nbf 
import os
import wget
import zipfile

def header_cell(author):
    # datetime object containing current date and time
    cells = []
    now = datetime.now()
    dt_string = now.strftime("on %d/%m/%Y at %H:%M:%S")

    source = [f'# MARKING NOTEBOOK [{author}]',
    f'### Generated {dt_string}']
    source = '\n'.join(source)

    cells.append(nbf.v4.new_markdown_cell(source=source))

    return cells

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
    f'sys.path.insert(0, f"../../grading/testing/notebook_tests")',
    f'sys.path.insert(1, f"../../grading/testing/external_tests")'
    ]
    
    source = '\n'.join(source)

    return nbf.v4.new_code_cell(source=source)
    
def footer_cell():
    lines = [f"nbta_test_style = QuestionGrader('style')",
    "nbta_estimated_mark = EstimatedMark()",
    f"nbta_private_feedback = QuestionGrader('Private_feedback_for_lecturer', feedback=True)"]
    return "\n".join(lines)

def download_data(id, google_drive=True, zip_name='raw_data.zip'):
    if google_drive:
        url = f'https://drive.google.com/uc?id={id}'
    else:
        url=id

    wget.download(url)

    with zipfile.ZipFile(zip_name, 'r',) as zip_ref:
        zip_ref.extractall()

    os.remove(zip_name)



class NotAssigned():
    def __init__(self,expected_type=''):
        self.expected_type = expected_type
        return None