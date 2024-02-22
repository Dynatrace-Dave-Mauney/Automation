# Rename JSON files for log ingest rules, and modify all the config.yaml references accordingly
# This way, human-readable names are used rather than cryptic UUIDs
# This technique likely also applies to other "Settings 2.0" Monaco folders, but has so far only been developed for:
# builtinlogmonitoring.log-storage-settings

import glob
import json
import os
import yaml

from json import JSONDecodeError
from Reuse import directories_and_files

INPUT_PATH = '/Dynatrace/Customers/ODFL/LogIngestionRules/Repo'


def load_file_name_lookup():
    file_name_lookup = {}
    for filename in glob.glob(INPUT_PATH + '/*.json'):
        if os.path.isfile(filename):
            if filename.endswith('.json'):
                with open(filename, 'r', encoding='utf-8') as f:
                    infile_content = f.read()
                    try:
                        infile_content_json = json.loads(infile_content)
                        config_item_title = infile_content_json.get('config-item-title')
                        clean_config_item_title = directories_and_files.get_clean_file_name(config_item_title, '_').replace(' ', '_')
                        monaco_id = os.path.basename(filename).replace('.json', '')
                        file_name_lookup[monaco_id] = clean_config_item_title
                    except JSONDecodeError:
                        print(f'Skipping due to non-JSON file content: {filename}')
            else:
                print(f'Skipping due to non-JSON file type: {filename}')

    return file_name_lookup


def rename_json_files(file_name_lookup):
    for old_monaco_id in file_name_lookup.keys():
        new_monaco_id = file_name_lookup[old_monaco_id]
        # if new_monaco_id != old_monaco_id:
        new_json_file_name = f'{INPUT_PATH}/{new_monaco_id}.json'
        old_json_file_name = f'{INPUT_PATH}/{old_monaco_id}.json'
        print(f'Renaming {old_json_file_name} to {new_json_file_name}')
        os.rename(old_json_file_name, new_json_file_name)


def modify_config_file(file_name_lookup):
    new_configs = []
    config_file_name = f'{INPUT_PATH}/config.yaml'
    yaml_dict = read_yaml(config_file_name)
    configs = yaml_dict.get('configs')
    for config in configs:
        # print(config)
        monaco_id = config.get('id')
        new_id = file_name_lookup.get(monaco_id)

        # print('New ID', new_id)

        new_config = config
        new_config['id'] = new_id
        new_config['config']['name'] = new_id
        new_config['config']['template'] = new_id + '.json'
        new_configs.append(new_config)

    # print(new_configs)

    yaml_dict['configs'] = new_configs
    write_yaml(yaml_dict, config_file_name)


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def write_yaml(any_dict, filename):
    with open(filename, 'w') as file:
        yaml.dump(any_dict, file, sort_keys=False)


def main():
    file_name_lookup = load_file_name_lookup()
    rename_json_files(file_name_lookup)
    modify_config_file(file_name_lookup)


if __name__ == '__main__':
    main()
