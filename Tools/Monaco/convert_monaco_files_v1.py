# Copy/rename json files and modify "template" references in config.yaml to new json file names
# The "name" in config.yaml is used for the new json file name

import json
import os
import shutil
import yaml

from Reuse import directories_and_files
from Reuse import environment

input_path = 'SET WITH CONFIGURATIONS YAML'
output_path = 'SET WITH CONFIGURATIONS YAML'

confirmation_required = False
remove_directory_at_startup = True
rename_files = True


def process():
    configuration_file = 'configurations.yaml'
    global input_path
    global output_path
    input_path = environment.get_configuration('convert_monaco_files_input_path', configuration_file=configuration_file)
    output_path = environment.get_configuration('convert_monaco_files_output_path', configuration_file=configuration_file)

    confirm('Convert monaco files from ' + input_path + ' to ' + output_path)
    initialize()

    new_configs = []
    old_config = read_yaml(f'{input_path}/config.yaml')
    configs = old_config['configs']

    # print(old_config)

    for config in configs:
        template = config['config']['template']
        # name = config['config']['name']
        # clean_file_name = directories_and_files.get_clean_file_name(name, '-')
        # output_filename = clean_file_name + '.json'
        # print(template, name, output_filename)

        copy_and_rename(f'{input_path}/{template}', f'{output_path}/{template}')

        config['config']['template'] = template
        new_configs.append(config)

    new_config_dict = {'configs': new_configs}
    write_yaml(new_config_dict, f'{output_path}/config.yaml')


def copy_and_rename(src_path, dest_path):
    json_data = read_json(src_path)
    title = json_data['title']
    # print(title)

    if title.startswith('SCRS - Purchase'):
        print(title)
        shutil.copy2(src_path, dest_path)

    if title.startswith('SCRS -  Purchase'):
        print(title)
        shutil.copy2(src_path, dest_path)


def update_config(new_config_dict, config_template, output_filename):
    old_id = config_template.replace('.json', '')
    new_config_dict['configs'][old_id]['config']['template'] = output_filename


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + output_path + ' directory will now be removed to prepare for the conversion.')
        directories_and_files.remove_directory(output_path)

    if not os.path.isdir(output_path):
        directories_and_files.make_directory(output_path)


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            print('Operation aborted')
            exit()


def read_json(input_file_name):
    with open(input_file_name, 'r', encoding='utf-8') as infile:
        json_data = json.loads(infile.read())
        return json_data


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
