# Put all dashboards in the specified directory to tenant/environment specified via command line argument.
# Can also be run in IDE with no command line arguments.
#

import json
import glob
import os
import requests
import ssl
import sys
import codecs


def run():
    """ For running directly from an IDE (or from a command line without using command line arguments) """
    # env_name, env, tenant, token = get_environment('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # path = '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    # path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000117.json'
    # path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000109.json'
    # path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000112.json'
    # path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000074.json'
    # path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-100000000000.json'
    # path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000???.json'
    # put_dashboards(env, token, path, env_name, get_owner())
    #
    # env_name, env, tenant, token = get_environment('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # path = '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    # put_dashboards(env, token, path, env_name, get_owner())
    #
    env_name, env, tenant, token = get_environment('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # path = '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    # path = 'Custom/Overview/00000000-dddd-bbbb-ffff-000000000001'
    # path = 'Custom/Overview/00000000-dddd-bbbb-ffff-000000000019'
    path = 'Custom/Overview/00000000-dddd-bbbb-ffff-00000000????'
    # path = 'Custom/Overview/00000000-dddd-bbbb-ffff-0000000010??'
    put_dashboards(env, token, path, env_name, get_owner())
    #
    # env_name, env, tenant, token = get_environment('FreeTrial1', 'FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN')
    # path = 'Custom/Overview/00000000-dddd-bbbb-ffff-00000000????'
    # put_dashboards(env, token, path, env_name, get_owner())


def get_environment(env_name, tenant_key, token_key):
    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    return env_name, env, tenant, token


def get_owner():
    return os.environ.get('DASHBOARD_OWNER_EMAIL', 'nobody@example.com')


def put_dashboard(env, token, dashboard_id, payload):
    url = env + '/api/config/v1/dashboards/' + dashboard_id
    print('PUT: ' + url)
    try:
        r = requests.put(url, payload.encode('utf-8'),
                         headers={'Authorization': 'Api-Token ' + token,
                                  'Content-Type': 'application/json; charset=utf-8'})
        # If you need to bypass certificate checks on managed and are ok with the risk:
        # r = requests.put(url, payload, headers=HEADERS, verify=False)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
    except ssl.SSLError:
        print('SSL Error')


def put_dashboards(env, token, path, prefix, owner):
    print('Prefix: ' + prefix)
    print('Owner:  ' + owner)
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            dashboard_id = dashboard_json.get('id')
            dashboard_name = dashboard_json.get('dashboardMetadata').get('name')
            dashboard_name = dashboard_name.replace('TEMPLATE:', prefix + ':')
            dashboard_name = dashboard_name.replace('BETA:', prefix + ':')
            dashboard_owner = dashboard_json.get('dashboardMetadata').get('owner')
            dashboard_owner = dashboard_owner.replace('nobody@example.com', owner)
            dashboard_owner = dashboard_owner.replace('Dynatrace', owner)
            print(filename + ': ' + dashboard_id + ': ' + dashboard_name)
            dashboard_json['dashboardMetadata']['name'] = dashboard_name
            dashboard_json['dashboardMetadata']['owner'] = dashboard_owner

            # TODO: Comment out temp code
            # Use these lines to modify id's to avoid overwrites
            dashboard_id = dashboard_id.replace('aaaaaaaa-bbbb-cccc-dddd-0', 'aaaaaaaa-bbbb-cccc-dddd-1')
            dashboard_json['id'] = dashboard_id

            tenant = env.split('.')[0].split('/')[2]

            new_tiles = []
            found = False
            tiles = dashboard_json.get('tiles')
            for tile in tiles:
                tile_type = tile.get('tileType')
                if tile_type == 'MARKDOWN':
                    tile_string = str(tile)
                    if '{{.tenant}}' in tile_string:
                        found = True
                        tile_string = tile_string.replace('{{.tenant}}', tenant)
                        new_tiles.append(eval(tile_string))
                    else:
                        new_tiles.append(tile)

            if found:
                dashboard_json['tiles'] = new_tiles

            put_dashboard(env, token, dashboard_id, json.dumps(dashboard_json))

            print(env + '/#dashboard;id=' + dashboard_id)


def main(arguments):
    usage = '''
    put_dashboards.py: Put dashboards from a file path to the tenant/environment.

    Usage:    put_dashboards.py <tenant/environment URL> <token> <path> <prefix> <owner>
    Examples: put_dashboards.py https://<TENANT>.live.dynatrace.com dt0c01.ABC.DEF /dashboards DEV nobody@example.com 
              put_dashboards.py https://<TENANT>.dynatrace-managed.com/e/<ENV> dt0c01.ABC.DEF /dashboards DEV nobody@example.com
    '''

    print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 2:
        print(usage)
        raise ValueError('Too few arguments!')
    if len(arguments) > 4:
        print(help)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 4:
            put_dashboards(arguments[1], arguments[2], arguments[3], arguments[3], arguments[4])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
