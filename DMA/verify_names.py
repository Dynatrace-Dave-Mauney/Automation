import json
import os
import re

from pathlib import Path

# Compare DMA Repo document file names to metadata names
DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards-Modified'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks-Modified'

DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks'


def main():
    try:
        # input_directory_name = DASHBOARD_REPO_PATH
        input_directory_name = NOTEBOOK_REPO_PATH

        for file_name in os.listdir(input_directory_name):
            if os.path.isfile(f'{input_directory_name}/{file_name}') and file_name.endswith('.metadata.json'):
                src = f'{input_directory_name}/{file_name}'
                stem = Path(file_name).stem
                stem = Path(stem).stem
                stem_prefix = re.sub('].*', '', stem)
                with open(src, 'r', encoding='utf-8') as infile:
                    input_string = infile.read()
                    input_json = json.loads(input_string)
                    name = input_json.get('name')
                    name_prefix = re.sub('].*', '', name)
                    if name_prefix != stem_prefix:
                        base_name = Path(file_name).name
                        print(f'Metadata name "{name_prefix}" not equal to file stem "{stem_prefix}": {base_name}')
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
