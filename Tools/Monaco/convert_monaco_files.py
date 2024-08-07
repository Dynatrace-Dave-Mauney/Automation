# Copy/rename json files and modify "template" references in config.yaml to new json file names
# The "name" in config.yaml is used for the new json file name

import os
import shutil
import yaml

from Reuse import directories_and_files

# INPUT_PATH = '\\Dynatrace\\Customers\\ODFL\\RequestAttributesUserPayloadExtracts\\request-attributes'
# OUTPUT_PATH = '\\Dynatrace\\Customers\\ODFL\\RequestAttributesUserPayloadExtracts\\request-attributes-names'
INPUT_PATH = 'C:\\Temp\\request-attributes'
OUTPUT_PATH = 'C:\\Temp\\request-attributes-preprod-improved'

confirmation_required = False
remove_directory_at_startup = True
rename_files = True


def process():
    confirm('Convert monaco files from ' + INPUT_PATH + ' to ' + OUTPUT_PATH)
    initialize()

    new_configs = []
    old_config = read_yaml(f'{INPUT_PATH}/config.yaml')
    configs = old_config['configs']

    for config in configs:
        template = config['config']['template']
        name = config['config']['name']
        clean_file_name = directories_and_files.get_clean_file_name(name, '-')
        output_filename = clean_file_name + '.json'
        # print(template, name, output_filename)
        copy_and_rename(f'{INPUT_PATH}/{template}', f'{OUTPUT_PATH}/{output_filename}')
        config['config']['template'] = output_filename
        new_configs.append(config)

    new_config_dict = {'configs': new_configs}
    write_yaml(new_config_dict, f'{OUTPUT_PATH}/config.yaml')


def copy_and_rename(src_path, dest_path):
    shutil.copy2(src_path, dest_path)


def update_config(new_config_dict, config_template, output_filename):
    old_id = config_template.replace('.json', '')
    new_config_dict['configs'][old_id]['config']['template'] = output_filename


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


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def write_yaml(any_dict, filename):
    with open(filename, 'w') as file:
        yaml.dump(any_dict, file, sort_keys=False)


def main():
    process()


if __name__ == '__main__':
    main()
