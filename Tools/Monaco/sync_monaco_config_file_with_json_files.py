import os
import glob
import json
import yaml

# configuration_yaml_file = '/Temp/builtinmonitoring.slo/config.yaml'
# input_glob_pattern = '/Temp/builtinmonitoring.slo/*.json'
# output_configuration_yaml_file = '/Temp/builtinmonitoring.slo/new_config.yaml'

configuration_yaml_file = '/Temp/builtinmanagement-zones-output/config.yaml'
input_glob_pattern = '/Temp/builtinmanagement-zones-output/*.json'
output_configuration_yaml_file = '/Temp/builtinmanagement-zones-output/new_config.yaml'


def main():
    ids_to_keep = []

    try:
        for file_name in glob.glob(input_glob_pattern, recursive=True):
            base_file_name = os.path.basename(file_name)
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    # formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    name = input_json.get('name')
                    # metric_expression = input_json.get('metricExpression')
                    # if '- Host Availability' in name:
                    if True:
                        id_to_keep = base_file_name.replace(".json", "")
                        # print(f'{name}: {metric_expression}:{id_to_keep}')
                        ids_to_keep.append(id_to_keep)
                        # print(formatted_json)
    except FileNotFoundError:
        print('The directory name does not exist')

    # print(ids_to_keep)

    new_config_dict_list = []
    config = get_config()

    # print(config)
    keep_count = 0
    config_dict_list = config.get('configs')
    for config_dict in config_dict_list:
        config_id = config_dict.get('id')
        if config_id in ids_to_keep:
            print(f'keep: {config_id}')
            new_config_dict_list.append(config_dict)
            keep_count += 1

    print(f'Kept {keep_count} configuration ids')

    new_config_dict = {'configs': new_config_dict_list}
    print(new_config_dict)
    write_yaml(new_config_dict, output_configuration_yaml_file)


def get_config():
    try:
        with open(configuration_yaml_file, 'r') as file:
            document = file.read()
            return yaml.load(document, Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}


def write_yaml(any_dict, filename):
    with open(filename, 'w') as file:
        yaml.dump(any_dict, file, sort_keys=False)


if __name__ == '__main__':
    main()
