import os
import glob
import yaml

configuration_yaml_file = '/Dynatrace/Customers/ODFL/RequestAttributesUserPayloadExtracts/request-attributes-names/config.yaml'
input_glob_pattern = '/Dynatrace/Customers/ODFL/RequestAttributesUserPayloadExtracts/request-attributes-names/*.json'
output_configuration_yaml_file = '/Dynatrace/Customers/ODFL/RequestAttributesUserPayloadExtracts/request-attributes-names/new_config.yaml'


def main():
    templates_to_keep = []

    try:
        for file_name in glob.glob(input_glob_pattern, recursive=True):
            base_file_name = os.path.basename(file_name)
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                template_to_keep = base_file_name
                # print(f'{name}: {metric_expression}:{id_to_keep}')
                templates_to_keep.append(template_to_keep)
                # print(formatted_json)
    except FileNotFoundError:
        print('The directory name does not exist')

    print(templates_to_keep)

    new_config_dict_list = []
    config = get_config()

    # print(config)
    keep_count = 0
    config_dict_list = config.get('configs')
    for config_dict in config_dict_list:
        config_template = config_dict['config']['template']
        print(config_template)
        if config_template in templates_to_keep:
            print(f'keep: {config_template}')
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
