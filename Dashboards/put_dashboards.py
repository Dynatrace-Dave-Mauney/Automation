# Put all dashboards matching the file path pattern to the specified environment.
# Parameters can be passed inline or from command line arguments.

import json
import glob
import os
import requests
import ssl
import sys
import codecs


supported_environments = {
    'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
    'FreeTrial1': ('FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN'),
}


def run():
    """ Used when running directly from an IDE (or from a command line without using command line arguments) """

    # Use the owner stored in properties by default.
    # Override it here or in the put_dashboard call, if needed.
    owner = get_owner()
    # owner = 'nobody@example.com'

    # Default prefix.
    # Override it here or in the put_dashboard call, if needed.
    prefix = ''

    # Put dashboard(s) to the environment name, path, prefix and owner specified.
    # Wildcards like "?" to signify any single character or "*" to signify any number of characters may be used.
    # When wildcards are used, multiple dashboards may be referenced.
    # Example Paths:
    #  Single file reference:
    #   '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    #   '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000117.json'
    #  Multiple file reference (potentially, it depends on the content of the directory):
    #   'Sandbox/00000000-dddd-bbbb-aaaa-????????????.json' # Strict reference
    #   'Sandbox/*.json' # Lenient reference

    # put_dashboards('Prod', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Prod', owner)
    # put_dashboards('Prep', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Prep', owner)
    # put_dashboards('Dev', '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json', 'Dev', owner)
    # put_dashboards('Personal', 'Sandbox/00000000-dddd-bbbb-aaaa-???????????1.json', 'Personal', owner)
    # put_dashboards('FreeTrial1', 'Sandbox/00000000-dddd-bbbb-aaaa-???????????1.json', 'Sandbox', owner)

    # put_dashboards('Personal', 'Templates/Overview/00000000-dddd-bbbb-ffff-????????????.json', 'Test', owner)
    # put_dashboards('Personal', 'Sandbox/00000000-dddd-bbbb-aaaa-????????????.json', 'Personal', owner)

    # put_dashboards('Dev', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Dev', owner)

    # put_dashboards('Prep', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Prep', owner)

    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json', 'Prod', owner)

    # owner = get_owner()
    # owner = 'xxxxxx@xxxxxxx.com'
    # put_dashboards('Personal', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000001???.json', 'Personal', owner)
    # put_dashboards('Dev', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000001???.json', 'Dev', owner)
    # put_dashboards('Prep', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000001???.json', 'Prep', owner)
    # put_dashboards('Prod', 'Templates/Overview/00000000-dddd-bbbb-ffff-000000001???.json', 'Prod', owner)


def put_dashboards(env_name, path, prefix, owner):
    print('Prefix: ' + prefix)
    print('Owner:  ' + owner)
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            dashboard_id = dashboard_json.get('id')
            dashboard_name = dashboard_json.get('dashboardMetadata').get('name')

            # Replace well-known placeholder prefixes or add a prefix, as needed
            new_prefix = ''
            if prefix and prefix != '':
                new_prefix = f'{prefix}: '
            if dashboard_name.startswith('TEMPLATE:'):
                dashboard_name = dashboard_name.replace('TEMPLATE: ', new_prefix)
            else:
                if dashboard_name.startswith('BETA:'):
                    dashboard_name = dashboard_name.replace('BETA: ', new_prefix)
                else:
                    dashboard_name = f'{new_prefix}{dashboard_name}'

            dashboard_owner = dashboard_json.get('dashboardMetadata').get('owner')
            dashboard_owner = dashboard_owner.replace('nobody@example.com', owner)
            dashboard_owner = dashboard_owner.replace('Dynatrace', owner)
            print(filename + ': ' + dashboard_id + ': ' + dashboard_name)
            dashboard_json['dashboardMetadata']['name'] = dashboard_name
            dashboard_json['dashboardMetadata']['owner'] = dashboard_owner

            # Enable "preset" for Dashboard Overview Framework
            if dashboard_id.startswith('00000000-dddd-bbbb-ffff'):
                print(f'Set preset to True for {dashboard_id}:{dashboard_name}')
                dashboard_json['dashboardMetadata']['preset'] = True

            # Temp code to modify IDs
            # dashboard_id = dashboard_id.replace('aaaaaaaa-bbbb-cccc-dddd-0', 'aaaaaaaa-bbbb-cccc-dddd-1')
            # dashboard_json['id'] = dashboard_id

            env, token = get_environment(env_name)
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


def get_owner():
    return os.environ.get('DASHBOARD_OWNER_EMAIL', 'nobody@example.com')


def get_environment(env_name):
    if env_name not in supported_environments:
        print(f'Invalid environment name: {env_name}')
        return None, None

    tenant_key, token_key = supported_environments.get(env_name)

    if env_name and tenant_key and token_key:
        tenant = os.environ.get(tenant_key)
        token = os.environ.get(token_key)
        env = f'https://{tenant}.live.dynatrace.com'

        if tenant and token and '.' in token:
            masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            print(f'Token:            {masked_token}')
            return env, token
        else:
            print('Invalid Environment Configuration!')
            print(f'Set the "env_name ({env_name}), tenant_key ({tenant_key}), token_key ({token_key})" tuple as required and verify the tenant ({tenant}) and token ({token}) environment variables are accessible.')
            exit(1)


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
            put_dashboards(arguments[1], arguments[2], arguments[3], arguments[3])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
