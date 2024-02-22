# First, manually modify the config.yaml file to reflect the desired rule order.
# Then, run this module to insert the required dependencies that insure the order is honored

import copy
import yaml


INPUT_PATH = '/Dynatrace/Customers/ODFL/LogIngestionRules/Repo'


def add_dependencies():
    dependency_parameters_template = {'order': {'configId': None, 'property': 'id', 'type': 'reference'}}
    config_file_name = f'{INPUT_PATH}/config.yaml'
    yaml_dict = read_yaml(config_file_name)
    configs = yaml_dict.get('configs')
    # print(configs)
    dependency_id = None
    new_configs = []
    for config in configs:
        monaco_id = config.get('id')
        if dependency_id:
            dependency_parameters = dependency_parameters_template
            dependency_parameters['order']['configId'] = dependency_id
            config['config']['parameters'] = copy.deepcopy(dependency_parameters)
            new_configs.append(config)
        else:
            try:
                config['config'].pop('parameters')
            except KeyError:
                print('No pop needed...')
            new_configs.append(config)
        dependency_id = monaco_id

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
    add_dependencies()


if __name__ == '__main__':
    main()
