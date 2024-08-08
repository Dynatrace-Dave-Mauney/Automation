import copy
import glob
import json
import os
from inspect import currentframe

CONFIGURATION_VERSION = 6
CLUSTER_VERSION = '1.261.134.20230302-084304'
DASHBOARD_NAME_PREFIX = 'TEMPLATE: '
OWNER = 'nobody@example.com'
SHARED = True
PRESET = False
FILTER = None
TILES_NAME_SIZE = 'small'
HAS_CONSISTENT_COLORS = True

DASHBOARD_GENERATED_PATH = f'../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-0000000000??.json'
DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'

confirmation_required = False

# Key is generated id and value is template id
id_conversion_dictionary = {
    'aaaaaaaa-bbbb-cccc-dddd-000000000002': '00000000-dddd-bbbb-ffff-000000001102',
    'aaaaaaaa-bbbb-cccc-dddd-000000000003': '00000000-dddd-bbbb-ffff-000000001103',
    'aaaaaaaa-bbbb-cccc-dddd-000000000004': '00000000-dddd-bbbb-ffff-000000001104',
    'aaaaaaaa-bbbb-cccc-dddd-000000000005': '00000000-dddd-bbbb-ffff-000000001105',
    'aaaaaaaa-bbbb-cccc-dddd-000000000006': '00000000-dddd-bbbb-ffff-000000001106',
    'aaaaaaaa-bbbb-cccc-dddd-000000000007': '00000000-dddd-bbbb-ffff-000000001107',
    'aaaaaaaa-bbbb-cccc-dddd-000000000008': '00000000-dddd-bbbb-ffff-000000001108',
    'aaaaaaaa-bbbb-cccc-dddd-000000000009': '00000000-dddd-bbbb-ffff-000000001109',
    'aaaaaaaa-bbbb-cccc-dddd-000000000010': '00000000-dddd-bbbb-ffff-000000001110',
    'aaaaaaaa-bbbb-cccc-dddd-000000000011': '00000000-dddd-bbbb-ffff-000000001111',
    'aaaaaaaa-bbbb-cccc-dddd-000000000012': '00000000-dddd-bbbb-ffff-000000001112',
    'aaaaaaaa-bbbb-cccc-dddd-000000000013': '00000000-dddd-bbbb-ffff-000000001113',
    'aaaaaaaa-bbbb-cccc-dddd-000000000014': '00000000-dddd-bbbb-ffff-000000001114',
    'aaaaaaaa-bbbb-cccc-dddd-000000000015': '00000000-dddd-bbbb-ffff-000000001115',
    'aaaaaaaa-bbbb-cccc-dddd-000000000016': '00000000-dddd-bbbb-ffff-000000001116',
    'aaaaaaaa-bbbb-cccc-dddd-000000000017': '00000000-dddd-bbbb-ffff-000000001117',
    'aaaaaaaa-bbbb-cccc-dddd-000000000018': '00000000-dddd-bbbb-ffff-000000001118',
    'aaaaaaaa-bbbb-cccc-dddd-000000000019': '00000000-dddd-bbbb-ffff-000000001119',
    'aaaaaaaa-bbbb-cccc-dddd-000000000020': '00000000-dddd-bbbb-ffff-000000001120',
    'aaaaaaaa-bbbb-cccc-dddd-000000000021': '00000000-dddd-bbbb-ffff-000000001121',
    'aaaaaaaa-bbbb-cccc-dddd-000000000022': '00000000-dddd-bbbb-ffff-000000001122',
    'aaaaaaaa-bbbb-cccc-dddd-000000000023': '00000000-dddd-bbbb-ffff-000000001123',
    'aaaaaaaa-bbbb-cccc-dddd-000000000024': '00000000-dddd-bbbb-ffff-000000001124',
    'aaaaaaaa-bbbb-cccc-dddd-000000000025': '00000000-dddd-bbbb-ffff-000000001125',
}


def customize_dashboards():
    print(f'DASHBOARD_NAME_PREFIX: {DASHBOARD_NAME_PREFIX}')
    print(f'OWNER:                 {OWNER}')
    print(f'CONFIGURATION_VERSION: {CONFIGURATION_VERSION}')
    print(f'CLUSTER_VERSION:       {CLUSTER_VERSION}')
    print(f'SHARED:                {SHARED}')
    print(f'PRESET:                {PRESET}')
    print(f'FILTER:                {FILTER}')
    print(f'TILES_NAME_SIZE:       {TILES_NAME_SIZE}')
    print(f'HAS_CONSISTENT_COLORS: {HAS_CONSISTENT_COLORS}')
    print('')

    confirm('Import dashboards from ' + DASHBOARD_GENERATED_PATH + ' to ' + DASHBOARD_TEMPLATE_PATH)

    for filename in glob.glob(DASHBOARD_GENERATED_PATH):
        base_name = os.path.basename(filename)

        dashboard_id = base_name.replace('.json', '')
        if dashboard_id in id_conversion_dictionary:
            with open(filename, 'r', encoding='utf-8') as f:
                dashboard = f.read()
                new_dashboard = customize_dashboard(dashboard)
                pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
                # name = new_dashboard.get('dashboardMetadata').get('name')
                new_dashboard_id = id_conversion_dictionary.get(dashboard_id)
                output_filename = f'{DASHBOARD_TEMPLATE_PATH}/{new_dashboard_id}.json'
                print(f'Converting "{filename}" to "{output_filename}"')
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    outfile.write(pretty_new_dashboard)
        # else:
        #     print(f'SKIPPING file name "{filename}" with base name "{base_name}" and dashboard id "{dashboard_id}"')



def customize_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    dashboard_id = dashboard_json.get('id')
    name = dashboard_json.get('dashboardMetadata').get('name')

    if new_dashboard_json.get('dashboardMetadata').get('sharingDetails', None):
        new_dashboard_json['dashboardMetadata'].pop('sharingDetails')

    if new_dashboard_json.get('dashboardMetadata').get('tags', None):
        new_dashboard_json['dashboardMetadata'].pop('tags')

    new_dashboard_json['metadata']['configurationVersions'] = [CONFIGURATION_VERSION]
    new_dashboard_json['metadata']['clusterVersion'] = CLUSTER_VERSION

    dashboard_id = new_dashboard_json.get('id')
    new_dashboard_id = id_conversion_dictionary.get(dashboard_id, dashboard_id)

    new_dashboard_json['id'] = new_dashboard_id

    new_dashboard_json['dashboardMetadata']['name'] = DASHBOARD_NAME_PREFIX + name
    new_dashboard_json['dashboardMetadata']['shared'] = SHARED
    new_dashboard_json['dashboardMetadata']['owner'] = OWNER
    new_dashboard_json['dashboardMetadata']['dashboardFilter'] = FILTER
    new_dashboard_json['dashboardMetadata']['preset'] = PRESET
    new_dashboard_json['dashboardMetadata']['tilesNameSize'] = TILES_NAME_SIZE
    new_dashboard_json['dashboardMetadata']['hasConsistentColors'] = HAS_CONSISTENT_COLORS

    max_left = 0
    tiles = new_dashboard_json.get('tiles')
    for tile in tiles:
        bounds = tile.get('bounds')
        left = bounds.get('left')
        width = bounds.get('width')
        new_left = left + width
        if new_left > max_left:
            max_left = new_left

    overview_back_button_left = 1368
    if max_left > overview_back_button_left:
        overview_back_button_left = max_left

    overview_back_button_tile = {
        "name": "Markdown",
        "tileType": "MARKDOWN",
        "configured": True,
        "bounds": {
            "top": 0,
            "left": overview_back_button_left,
            "width": 152,
            "height": 38
        },
        "tileFilter": {},
        "markdown": "#### [\u21e6 Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\n![BackButton]()"
    }

    tiles.append(overview_back_button_tile)

    return new_dashboard_json


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_linenumber())


def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno


def main():
    customize_dashboards()


if __name__ == '__main__':
    main()
