from bs4 import BeautifulSoup
import json
from os import listdir
from os.path import isfile, join

class htmlToIpnb:
    def __init__(self,folder='../raw_data/htmls'):
        self.folder=folder
        
    def convert_file(self, file_name):
        response = open(f"{self.folder}/{file_name}")
        text = response.read()

        soup = BeautifulSoup(text, 'lxml')
        dictionary = {'nbformat': 4, 'nbformat_minor': 1, 'cells': [], 'metadata': {}}
        for d in soup.findAll("div"):
            if 'class' in d.attrs.keys():
                for clas in d.attrs["class"]:
                    if clas in ["text_cell_render", "input_area"]:
                    # code cell
                        if clas == "input_area":
                            cell = {}
                            cell['metadata'] = {}
                            cell['outputs'] = []
                            cell['source'] = [d.get_text()]
                            cell['execution_count'] = None
                            cell['cell_type'] = 'code'
                            dictionary['cells'].append(cell)

                        else:
                            cell = {}
                            cell['metadata'] = {}

                            cell['source'] = [d.decode_contents()]
                            cell['cell_type'] = 'markdown'
                            dictionary['cells'].append(cell)
        notebook_name=f"{self.folder}/{file_name.strip('.html')}.ipynb"
        
        open(notebook_name, 'w').write(json.dumps(dictionary))
        print(f'Notebook {notebook_name} succesfully created')
        
        return None
    
    
    def convert(self):
        htmls = [f for f in listdir(self.folder) if f.split('.')[-1]=='html']
        for html in htmls:
            self.convert_file(html)
        
        print(f'Converted {len(htmls)} files.')
        
        return None

if __name__ == '__main__':
    htmlToIpnb().convert()
        
