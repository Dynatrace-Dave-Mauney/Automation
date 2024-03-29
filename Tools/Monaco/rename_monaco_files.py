# Deprecated: use "convert_monaco_files.py" instead

import glob
import os
import shutil
import yaml

from pathlib import Path
from Reuse import directories_and_files

# INPUT_PATH = '/Temp/Monaco'
# INPUT_PATH = '/tools/monaco20-ODFL-Dev-DOWNLOAD/download_2024-02-12-153329//project_ODFL_Dev/builtinlogmonitoring.log-storage-settings'
# INPUT_PATH = '/tools/monaco20-ODFL-PreProd-DOWNLOAD//download_2024-02-12-154729/project_ODFL_PreProd/builtinlogmonitoring.log-storage-settings'
# INPUT_PATH = '/tools/monaco20-ODFL-Prod-DOWNLOAD/download_2024-02-12-154942/project_ODFL_Prod/builtinlogmonitoring.log-storage-settings'
# OUTPUT_PATH = '/Temp/Monaco-Renames'
# INPUT_PATH = 'C:\\tools\\monaco20-Dave-MyTenant-DOWNLOAD\\download_2024-03-06-151807\\project_myTenant\\request-attributes'
# OUTPUT_PATH = 'C:\\tools\\monaco20-Dave-MyTenant-DOWNLOAD\\download_2024-03-06-151807\\project_myTenant\\request-attributes-improved'
INPUT_PATH = 'C:\\Temp\\request-attributes'
OUTPUT_PATH = 'C:\\Temp\\request-attributes-improved'

confirmation_required = False
remove_directory_at_startup = True
rename_files = True


def copy_selected_files():
    confirm('Copy selected files from ' + INPUT_PATH + ' to ' + OUTPUT_PATH)
    initialize()

    for filename in glob.glob(INPUT_PATH + '/*'):
        if os.path.isfile(filename):
            process_file(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_directory(path):
    for filename in glob.glob(path + '/*.json'):
        if os.path.isfile(filename):
            process_file(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_file(filename):
    print(f'Processing {filename}')

    if filename.endswith('.json'):
        template_to_name_lookup = load_template_to_name_lookup()
        config_template = os.path.basename(filename)
        config_name = template_to_name_lookup[config_template]
        clean_file_name = directories_and_files.get_clean_file_name(config_name, '-')
        output_filename = clean_file_name + '.json'
        copy_and_rename(f'{INPUT_PATH}/{config_template}', f'{OUTPUT_PATH}/{output_filename}')
    else:
        # Just copy file and leave name unchanged
        copy_and_rename(f'{INPUT_PATH}/{os.path.basename(filename)}', f'{OUTPUT_PATH}/{os.path.basename(filename)}')


def load_template_to_name_lookup():
    template_to_name_lookup = {}
    yaml_dict = read_yaml(f'{INPUT_PATH}/config.yaml')
    configs = yaml_dict['configs']

    for config in configs:
        config_template = config['config']['template']
        config_name = config['config']['name']
        template_to_name_lookup[config_template] = config_name

    return template_to_name_lookup


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def copy_and_rename(src_path, dest_path):
    shutil.copy2(src_path, dest_path)


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + OUTPUT_PATH + ' directory will now be removed to prepare for the conversion.')
        directories_and_files.remove_directory(OUTPUT_PATH)

    if not os.path.isdir(OUTPUT_PATH):
        directories_and_files.make_directory(OUTPUT_PATH)


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            print('Operation aborted')
            exit()


def main():
    copy_selected_files()


if __name__ == '__main__':
    main()
