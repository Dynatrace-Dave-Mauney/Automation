"""

Compare dashboards using Winmerge (or a simliar tool) by downloading from a tenant or copying from a
directory while optionally filtering on specified criteria.

NOTE: There are typically so many differences between an initial dashboard JSON file and a downloaded one
that it makes the most sense to download a "pristine" copy after putting the last version to the tenant,
and then compare subsequent iterations to the pristine copy.

"""

import json
import glob
import os.path

from Reuse import directories_and_files
from Reuse import dynatrace_api
from Reuse import environment


left_output_path = 'compare/left'
right_output_path = 'compare/right'


def compare(**kwargs):
    if not kwargs:
        print('Must provide a left and right env/path: Examples: "left_path", "right_path", "left_env", "right_env"')
        exit(1)

    left_path = kwargs.get('left_path')
    right_path = kwargs.get('right_path')
    left_env = kwargs.get('left_env')
    right_env = kwargs.get('right_env')
    left_token = kwargs.get('left_token')
    right_token = kwargs.get('right_token')

    left_side_dashboard_list = load(left_path, left_env, left_token)
    right_side_dashboard_list = load(right_path, right_env, right_token)

    if os.path.isdir(left_output_path):
        directories_and_files.remove_directory(left_output_path)

    if os.path.isdir(right_output_path):
        directories_and_files.remove_directory(right_output_path)

    directories_and_files.make_directory(left_output_path)
    directories_and_files.make_directory(right_output_path)

    for left_side_dashboard in left_side_dashboard_list:
        filename = left_side_dashboard.get('id') + '.json'
        write_json(left_output_path, filename, left_side_dashboard)

    for right_side_dashboard in right_side_dashboard_list:
        filename = right_side_dashboard.get('id') + '.json'
        write_json(right_output_path, filename, right_side_dashboard)


def load(load_path, load_env, load_token):
    if load_path:
        return load_from_path(load_path)
    else:
        return load_from_environment(load_env, load_token)


def load_from_path(path_to_load):
    ignore_list = [
        '00000000-dddd-bbbb-ffff-000000000001.json',
        '00000000-dddd-bbbb-ffff-000000000001-v1.json',
        '00000000-dddd-bbbb-ffff-000000000001-v2.json',
        '00000000-dddd-bbbb-ffff-000000000001-v2a.json',
        '00000000-dddd-bbbb-ffff-000000000001-v3.json',
        '00000000-dddd-bbbb-ffff-000000000001-v3a.json',
        '00000000-dddd-bbbb-ffff-000000000001-v3b.json',
        '00000000-dddd-bbbb-ffff-000000000014.json',
        '00000000-dddd-bbbb-ffff-000000000800.json',
        '00000000-dddd-bbbb-ffff-000000000800-v1.json',
        '00000000-dddd-bbbb-ffff-000000000807.json',
        '00000000-dddd-bbbb-ffff-000000000900.json',
    ]

    load_list = []
    for filename in glob.glob(path_to_load):
        if os.path.basename(filename) not in ignore_list:
            with open(filename, 'r', encoding='utf-8') as f:
                dashboard = json.loads(f.read())
                load_list.append(dashboard)
    
    return load_list


def load_from_environment(env_to_load, env_token):
    load_list = []
    endpoint = '/api/config/v1/dashboards'
    dashboard_json_list = dynatrace_api.get_json_list_with_pagination(f'{env_to_load}{endpoint}', env_token)
    for dashboard_json in dashboard_json_list:
        inner_dashboard_json_list = dashboard_json.get('dashboards')
        for inner_dashboard_json in inner_dashboard_json_list:
            dashboard_id = inner_dashboard_json.get('id')
            # dashboard_name = inner_dashboard_json.get('name')
            if dashboard_id.startswith('00000000-dddd-bbbb-ffff-0'):
                r = dynatrace_api.get_without_pagination(f'{env_to_load}{endpoint}/{dashboard_id}', env_token)
                dashboard = r.json()
                load_list.append(dashboard)

    return load_list


def write_json(directory_path, filename, json_dict):
    # print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
    file_path = directory_path + '/' + filename
    with open(file_path, 'w') as file:
        file.write(json.dumps(json_dict, indent=4, sort_keys=False))


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    _, env, token = environment.get_environment_for_function('Prod', friendly_function_name)

    compare(left_path='Custom/Overview-Prod/00000000-dddd-bbbb-ffff-0*.json', right_env=env, right_token=token)


if __name__ == '__main__':
    main()
