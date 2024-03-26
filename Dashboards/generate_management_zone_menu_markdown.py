# import copy
# import json
# import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    endpoint = '/api/config/v1/managementZones'
    management_zone_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    markdown = '"markdown": "Management Zone Overview Links\n\n'

    link_list = []
    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            mz_id = inner_management_zone_json.get('id')
            mz_name = inner_management_zone_json.get('name')
            dashboard_id = convert_mz_id_to_db_id(mz_id)
            # print(mz_id, mz_name, dashboard_id)
            markdown += f'[{mz_name}](#dashboard;id={dashboard_id};gf={mz_id})  \n'

    print(markdown)


def convert_mz_id_to_db_id(mz_id):
    # drop the negative sign, if present and start number with 1 instead.
    # start positive numbers with 2 so that positive and negative numbers are both of the same length (20) and remain unique.
    if mz_id.startswith('-'):
        mz_id = '1' + mz_id.replace('-', '')
    else:
        mz_id = '2' + mz_id

    mz_id_string = str(mz_id)
    dashboard_id = f'00000000-dddd-{mz_id_string[0:4]}-{mz_id_string[4:8]}-{mz_id_string[8:20]}'

    return dashboard_id


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
