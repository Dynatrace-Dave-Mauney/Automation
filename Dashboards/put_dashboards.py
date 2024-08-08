# Put all dashboards matching the file path pattern to the specified environment.
# Parameters can be passed inline or from command line arguments.

import json
import glob
import os
import sys
import codecs

from Reuse import dynatrace_api
from Reuse import environment


def run():
    """ Used when running directly from an IDE (or from a command line without using command line arguments) """

    # Use the owner stored in properties by default.
    # Override it here or in the put_dashboard call, if needed.
    # owner = 'nobody@example.com'
    owner = get_owner()

    # Default prefix.
    # Override it here or in the put_dashboard call, if needed.
    # prefix = ''

    current_customer_skip_list = [
        ': Azure',
        # ': Microsoft SQL Server',
        ': Palo Alto',
        ': Redis',
        ': SAP',
        ': SOLR',
        ': WebLogic',
    ]

    # LAST-MONTH-JULY2024-current_customer_skip_list = [
    #     ': AWS',
    #     ': DB2',
    #     ': IBM',
    #     ': Oracle',
    #     ': SAP',
    #     ': SOLR',
    #     # ': VMware',
    #     ': Weblogic',
    #     ': WebSphere',
    # ]
    #
    # Customer-1 skips
    # current_customer_skip_list = [
    #     ': AWS',
    #     ': Azure',
    #     ': DB2',
    #     ': F5',
    #     ': IBM',
    #     ': Kafka',
    #     ': Microsoft',
    #     ': Oracle',
    #     ': SAP',
    #     ': SOLR',
    #     ': VMware',
    #     ': WebSphere',
    # ]
    #
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

    # Example Paths
    # '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    # 'Sandbox/00000000-dddd-bbbb-aaaa-???????????1.json'
    # 'Templates/Overview/00000000-dddd-bbbb-ffff-000000000807-v1.json'
    # 'Curated/Extensions/SQLServer/*SQL Server*.json'
    # '../DynatraceDashboardGenerator/aaaaaaaa-aaaa-aaaa-aaaa-00000000000?.json'
    # '../$Output/Dashboards/Downloads/Prod/*.json'

    # env_name = 'Prod'
    # env_name = 'PreProd'
    # env_name = 'Dev'
    # env_name = 'Personal'
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-*.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v3c.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000014-v1.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000800-v2.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000900-v1.json', owner=owner, skip_list=current_customer_skip_list)

    # env_name = 'Prod'
    # env_name = 'PreProd'
    # env_name = 'Dev'
    # env_name = 'Personal'
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v3c.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000033.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000034.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000035.json', owner=owner, skip_list=current_customer_skip_list)

    # PRIOR CUSTOMER!
    # env_name = 'Upper'
    # env_name = 'Lower'
    # env_name = 'Sandbox'
    # env_name = 'Prod  '
    # env_name = 'PreProd'
    # env_name = 'Dev'
    # env_name = 'Personal'
    # Overview and Children
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-*.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000800-v3.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000900-v2.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000110-v1.json', owner=owner, skip_list=current_customer_skip_list)

    # Generated Dashboards
    # put_dashboards(env_name, f'../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-*.json', owner=owner, skip_list=current_customer_skip_list)

    # New Self-Monitoring
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000800-v3.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-00000000082?.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000820.json', owner=owner, skip_list=current_customer_skip_list)

    # Azure Home
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000110.json', owner=owner, skip_list=current_customer_skip_list)

    # Google Home
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000130.json', owner=owner, skip_list=current_customer_skip_list)

    # Overview
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4.json', owner=owner, skip_list=current_customer_skip_list)

    # Overview/F5/Redis/Palo Alto OOTB Link
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4_{env_name}.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000046.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000050.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000051.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000052.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000053.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000054.json', owner=owner, skip_list=current_customer_skip_list)

    # Administration dashboard improvements
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000800-v3.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000813.json', owner=owner, skip_list=current_customer_skip_list)

    # Added Queues dashboard, and make use of the environment-specific menu
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4_{env_name}.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000036.json', owner=owner, skip_list=current_customer_skip_list)

    # Revert Host and Process Dashboards (removing availability, which has a "current datapoint cliff" issue)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000008.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000009.json', owner=owner, skip_list=current_customer_skip_list)

    # Add "Calls To Databases"
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4_{env_name}.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000037.json', owner=owner, skip_list=current_customer_skip_list)

    # Add "VMware"
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4_{env_name}.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000048.json', owner=owner, skip_list=current_customer_skip_list)

    # CURRENT CUSTOMER!
    # env_name = 'Prod'
    # env_name = 'NonProd'
    # env_name = 'Sandbox'
    # Overview and Children
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-*.json', owner=owner, skip_list=current_customer_skip_list)

    # Overrides are no longer needed as the customization step should take care of it now...
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4_Prod.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000800-v3.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000900-v2.json', owner=owner, skip_list=current_customer_skip_list)

    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000001-v4_Prod.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000038.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000058.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000068.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000098.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000100.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000147.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000148.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000802.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000000803.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000001000.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000001024.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-000000001025.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'Custom/Overview-{env_name}/00000000-dddd-bbbb-ffff-0000000011??.json', owner=owner, skip_list=current_customer_skip_list)

    # Generated Dashboards
    # put_dashboards(env_name, f'../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000000.json', owner=owner, skip_list=current_customer_skip_list)
    # put_dashboards(env_name, f'../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-*.json', owner=owner, skip_list=current_customer_skip_list)


def put_dashboards(env_name, path, **kwargs):
    prefix = kwargs.get('prefix')
    owner = kwargs.get('owner')
    skip_list = kwargs.get('skip_list', [])

    print(f'Prefix:    {prefix}')
    print(f'Owner:     {owner}')
    # print(f'Skip List: {skip_list}')

    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            dashboard_id = dashboard_json.get('id')
            dashboard_name = dashboard_json.get('dashboardMetadata').get('name')

            # Skip any dashboards that are in the "skip list"
            skip_dashboard = False
            for skip in skip_list:
                if skip in dashboard_name:
                    print(f'Skipping {dashboard_name} due to match found in skip list')
                    skip_dashboard = True
                    break
            if skip_dashboard:
                continue

            if prefix:
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

                dashboard_json['dashboardMetadata']['name'] = dashboard_name

            if owner:
                dashboard_owner = dashboard_json.get('dashboardMetadata').get('owner')
                dashboard_owner = dashboard_owner.replace('nobody@example.com', owner)
                dashboard_owner = dashboard_owner.replace('Dynatrace', owner)
                dashboard_json['dashboardMetadata']['owner'] = dashboard_owner
            # print(filename + ': ' + dashboard_id + ': ' + dashboard_name)

            # Enable "preset" for Dashboard Overview Framework
            if dashboard_id.startswith('00000000-dddd-bbbb-ffff'):
                # print(f'Set preset to True for {dashboard_id}:{dashboard_name}')
                dashboard_json['dashboardMetadata']['preset'] = True

            # # Disable "preset" for Dashboard Overview Framework
            # if dashboard_id.startswith('00000000-dddd-bbbb-ffff'):
            #     print(f'Set preset to False for {dashboard_id}:{dashboard_name}')
            #     dashboard_json['dashboardMetadata']['preset'] = False

            # Temp code to modify IDs
            # dashboard_id = dashboard_id.replace('aaaaaaaa-bbbb-cccc-dddd-0', 'aaaaaaaa-bbbb-cccc-dddd-1')
            # dashboard_json['id'] = dashboard_id

            _, env, token = environment.get_environment(env_name)
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

            print(f'{env}/#dashboard;id={dashboard_id}')


def get_owner():
    return os.environ.get('DYNATRACE_DASHBOARD_OWNER', 'nobody@example.com')


def put_dashboard(env, token, dashboard_id, payload):
    endpoint = '/api/config/v1/dashboards'
    dynatrace_api.put_object(f'{env}{endpoint}/{dashboard_id}', token, payload)


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
            put_dashboards(arguments[1], arguments[2], prefix=arguments[3], owner=arguments[3])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
