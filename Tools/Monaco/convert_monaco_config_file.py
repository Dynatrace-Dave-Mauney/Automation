# Deprecated: use "convert_monaco_files.py" instead

import glob
import os
import yaml
# import shutil
# from json import JSONDecodeError

# from Reuse import directories_and_files

INPUT_PATH1 = '/tools/monaco20-ODFL-Dev-DOWNLOAD/download_2024-02-12-153329//project_ODFL_Dev/builtinlogmonitoring.log-storage-settings/config.yaml'
INPUT_PATH2= '/tools/monaco20-ODFL-PreProd-DOWNLOAD//download_2024-02-12-154729/project_ODFL_PreProd/builtinlogmonitoring.log-storage-settings/config.yaml'
INPUT_PATH3= '/tools/monaco20-ODFL-Prod-DOWNLOAD/download_2024-02-12-154942/project_ODFL_Prod/builtinlogmonitoring.log-storage-settings/config.yaml'
OUTPUT_PATH = '/Temp/Monaco-Renames'

filename_list = [INPUT_PATH1, INPUT_PATH2, INPUT_PATH3]


def load_output_json_file_information():
    entity_id_list = []
    for filename in glob.glob(OUTPUT_PATH + '/*.json'):
        entity_id = os.path.basename(filename).replace('.json', '')
        entity_id_list.append(entity_id)

    return entity_id_list


def generate_config_file(filename_list):
    json_entity_id_list = load_output_json_file_information()
    process_config_file(filename_list, json_entity_id_list)


def process_config_file(filename_list, json_entity_id_list):
    new_yaml_dict = {'configs': []}
    for filename in filename_list:
        with open(filename, 'r', encoding='utf-8') as f:
            yaml_dict = read_yaml(filename)
            for entity_dict in yaml_dict.get('configs'):
                entity_id = entity_dict.get('id')
                if entity_id in json_entity_id_list:
                    new_yaml_dict['configs'].append(entity_dict)

    write_yaml(new_yaml_dict, f'{OUTPUT_PATH}/{os.path.basename(filename)}')


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def write_yaml(any_dict, filename):
    with open(filename, 'w') as file:
        yaml.dump(any_dict, file, sort_keys=False)


def main():
    generate_config_file(filename_list)


if __name__ == '__main__':
    main()
