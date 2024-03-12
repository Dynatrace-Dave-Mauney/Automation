import glob
import json
import os
# import shutil
from json import JSONDecodeError

from Reuse import directories_and_files

# INPUT_PATH = '/Temp/Monaco'
# INPUT_PATH = '/tools/monaco20-ODFL-Dev-DOWNLOAD/download_2024-02-12-153329//project_ODFL_Dev/builtinlogmonitoring.log-storage-settings'
# INPUT_PATH = '/tools/monaco20-ODFL-PreProd-DOWNLOAD//download_2024-02-12-154729/project_ODFL_PreProd/builtinlogmonitoring.log-storage-settings'
# INPUT_PATH = '/tools/monaco20-ODFL-Prod-DOWNLOAD/download_2024-02-12-154942/project_ODFL_Prod/builtinlogmonitoring.log-storage-settings'
# OUTPUT_PATH = '/Temp/Monaco-Renames'
INPUT_PATH = 'C:\\tools\\monaco20-Dave-MyTenant-DOWNLOAD\\download_2024-03-06-151807\\project_myTenant\\request-attributes'
OUTPUT_PATH = 'C:\\tools\\monaco20-Dave-MyTenant-DOWNLOAD\\download_2024-03-06-151807\\project_myTenant\\request-attributes-improved'


confirmation_required = False
remove_directory_at_startup = False
rename_files = True


def copy_selected_files():
    confirm('Copy selected files from ' + INPUT_PATH + ' to ' + OUTPUT_PATH)
    initialize()

    for filename in glob.glob(INPUT_PATH + '/*.json'):
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
    # print(f'Processing {filename}')

    with open(filename, 'r', encoding='utf-8') as f:
        if filename.endswith('.json'):
            infile_content = f.read()
            try:
                infile_content_json = json.loads(infile_content)
                print(infile_content_json)
                # key = infile_content_json.get('key')
                # key = infile_content_json.get('name')
                # key = infile_content_json.get('config-item-title')
                data_sources = infile_content_json.get('dataSources')
                source = data_sources[0].get('source')
                parameter_name = data_sources[0].get('parameterName', 'None')
                key = source + '-' + parameter_name
                if '[Built-in]' not in key:
                    clean_file_name = directories_and_files.get_clean_file_name(key, '-')
                    # print(key)
                    if rename_files:
                        output_filename = f'{OUTPUT_PATH}/{clean_file_name}.json'
                    else:
                        output_filename = f'{OUTPUT_PATH}/{os.path.basename(filename)}'
                    print(output_filename, clean_file_name)
                    with open(output_filename, 'w', encoding='utf-8') as outfile:
                        # To pretty print JSON:
                        # outfile.write(json.dumps(infile_content_json, indent=4, sort_keys=False))
                        # To write file as is
                        # print(infile_content)
                        outfile.write(infile_content)
            except JSONDecodeError:
                print(f'Skipping due to non-JSON file content: {filename}')
        else:
            print(f'Skipping due to non-JSON file type: {filename}')


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
