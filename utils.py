from datetime import datetime
import nbformat as nbf 

def header_cell(author):
    # datetime object containing current date and time
    now = datetime.now()
    dt_string = now.strftime("on %d/%m/%Y at %H:%M:%S")

    source = [f'# MARKING NOTEBOOK [{author}]',
    f'### Generated {dt_string}']
    source = '\n'.join(source)
    return nbf.v4.new_markdown_cell(source=source)

def header_code_cell(author):
    source = [f'import nbta',
    'import numpy as np',
    'import pandas as pd',
    'import matplotlib.pyplot as plt']
    
    source = '\n'.join(source)
    return nbf.v4.new_code_cell(source=source)


class NotAssigned():
    def __init__(self,expected_type=''):
        self.expected_type = expected_type
        return None