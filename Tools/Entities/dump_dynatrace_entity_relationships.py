#
# For the entities specified via command line argument, dump the relationships with all dependencies to a file and dump each
# entity to a file in json format.
#
# The output can then be compared to prior output to detect any changes to the dependencies.
#

import json
import os
import requests
import sys
# import urllib3

PATH = '../../$Output/Tools/Entities/Relationships'

# If "verify=False" is used on "requests.get" calls, do not print warnings
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# indent = 0
outfile = open(PATH + '/dynatrace_entity_relationships.txt', 'w')

entities_written = []
services_encountered = []


def get_rest_api_json(url, token, endpoint, params, verify):
    # print(f'get_rest_api_json({url}, {endpoint}, {params})')
    full_url = url + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token}, verify=verify)
    # print(f'GET {full_url} {resp.status_code} - {resp.reason}')
    if resp.status_code != 200:
        print('REST API Call Failed!')
        print(f'GET {resp.url} {resp.status_code} - {resp.reason}')
        exit(1)
    return resp.json()


def get_entity_stack(url, token, verify, entities, level):

    global services_encountered
    global entities_written

    # print(f'entities: {entities}')
    indent = ' ' * level
    level_in = level
    for entity in entities:

        # To avoid infinite loops, skip services already seen
        if entity.startswith('SERVICE') and entity in services_encountered:
            continue

        # print(f'level: {level}')
        # print(f'entity: {entity}')
        endpoint = '/api/v2/entities/' + entity
        params = ''
        entity_json = get_rest_api_json(url, token, endpoint, params, verify)
        entity_id = entity_json.get('entityId')
        display_name = entity_json.get('displayName')
        print(indent + entity_id + ':' + display_name)
        print(indent + entity_id + ':' + display_name, file=outfile)

        if entity_id.startswith('SERVICE') and entity_id not in services_encountered:
            services_encountered.append(entity_id)

        if entity_id not in entities_written:
            entities_written.append(entity_id)
            entityfile = open(PATH + '/' + entity_id + '.json', 'w')
            print(json.dumps(entity_json, indent=4), file=entityfile)
            entityfile.close()

        runs_on_child_entities = []
        runs_on_child_dicts = entity_json.get('fromRelationships').get('runsOn')
        # print(runs_on_child_dicts)
        if runs_on_child_dicts:
            print(indent + 'Runs On:')
            print(indent + 'Runs On:', file=outfile)
            for runs_on_child_dict in runs_on_child_dicts:
                # print(calls_child_dict)
                entity_id = runs_on_child_dict.get('id')
                if entity_id:
                    runs_on_child_entities.append(entity_id)
            get_entity_stack(url, token, verify, runs_on_child_entities, level)

        calls_child_entities = []
        calls_child_dicts = entity_json.get('fromRelationships').get('calls')
        # print(calls_child_dicts)
        if calls_child_dicts:
            print(indent + 'Calls:')
            print(indent + 'Calls:', file=outfile)
            level += 1
            for calls_child_dict in calls_child_dicts:
                # print(calls_child_dict)
                entity_id = calls_child_dict.get('id')
                if entity_id:
                    calls_child_entities.append(entity_id)
            get_entity_stack(url, token, verify, calls_child_entities, level)
        level = level_in

        # Reset for next "root entity"
        if level == 0:
            services_encountered = []


def process(env, token, verify, entity_list_string):
    # Assume tenant/environment URL followed by Token
    root_entities = entity_list_string.split(',')
    level = 0

    print('env: ' + env)
    print('token: ' + token[0:31] + '.*' + ' (masked for security)')

    get_entity_stack(env, token, verify, root_entities, level)

    print('')
    print(f'Relationship details were written to {outfile.name}')

    print(f'{len(entities_written)} dependencies were written to json files:')
    for entity in (sorted(entities_written)):
        print(entity + '.json')

    if not verify:
        print('')
        print('WARNING: You are not verifying the server certificate!')


def run():
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    service = 'SERVICE-5946F26F5835488B'

    process(env, token, verify=True, entity_list_string=service)


def main(arguments):
    help_text = '''
    dump_dynatrace_entity_relationships.py Dumps the "fromRelationships" for a specified list of entities.  
    Output is written to one file for the relationships, and each dependency is dumped to a JSON file.

    Usage:    dump_dynatrace_entity_relationships.py <tenant/environment URL> <token> <entity_list> <verify>
    Examples: dump_dynatrace_entity_relationships.py https://TENANTID.live.dynatrace.com <TOKEN> <entity_list> <verify>
              dump_dynatrace_entity_relationships.py https://TENANTID.dynatrace-managed.com/e/<ENV_ID> <TOKEN> <entity_list> <verify>
              
              dump_dynatrace_entity_relationships.py https://abc12345.live.dynatrace.com BrYrbLOABC2R0hj00nlox True APPLICATION-25C40310FED87AF0,APPLICATION-BD398CC2DBED6B0F
    '''

    # print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 4:
        print(help_text)
        raise ValueError('Too few arguments!')
    if len(arguments) > 5:
        print(help_text)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help_text)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 5:
            if arguments[3] not in ('True', 'False'):
                print(help_text)
                raise ValueError('Verify must be one of "True" or "False"')
            process(env=arguments[1], token=arguments[2], verify=arguments[3], entity_list_string=arguments[4])
        else:
            print(help_text)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
