import glob
import json
import os
import shutil
from inspect import currentframe
from json import JSONDecodeError

# DASHBOARD_INPUT_PATH = '../$Input/Dashboards/Cleaner'
# DASHBOARD_OUTPUT_PATH = '../$Output/Dashboards/Cleaned'

DASHBOARD_INPUT_PATH = 'Templates/Overview'
DASHBOARD_OUTPUT_PATH = 'Templates-Overview-Clean'

# DASHBOARD_INPUT_PATH = 'Templates-Overview-Clean'
# DASHBOARD_OUTPUT_PATH = 'Templates-Overview-Reclean'

confirmation_required = True
remove_directory_at_startup = True

current_cluster_version = '1.261.134.20230302-084304'
current_configuration_versions = [6]

file_skip_list = [
    'Templates/Overview\README.md',
    'Templates/Overview\dashboard_index_by_id.txt',
    'Templates/Overview\dashboard_index_by_name.txt',
    'Templates/Overview\dashboard_templates_overview_versions.txt',
    'Templates/Overview\demo_dashboard_index_by_id.txt',
    'Templates/Overview\demo_dashboard_notes.txt',
    'Templates/Overview\markdown_aws_menu.json',
    'Templates/Overview\markdown_menu-BACKUP.json',
    'Templates/Overview\markdown_menu-v1.json',
    'Templates/Overview\markdown_menu.json',
]

def clean_dashboards():
    confirm('clean dashboards from ' + DASHBOARD_INPUT_PATH + ' to ' + DASHBOARD_OUTPUT_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_INPUT_PATH + '/*'):
        if os.path.isfile(filename):
            clean_dashboard(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_directory(path):
    for filename in glob.glob(path + '/*'):
        if os.path.isfile(filename):
            clean_dashboard(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def clean_dashboard(filename):
    # print(f'Processing {filename}')

    fixes = []
    id_index = 1

    with open(filename, 'r', encoding='utf-8') as f:
        dashboard = f.read()
        try:
            dashboard_json = json.loads(dashboard)
            metadata = dashboard_json.get('metadata')
            cluster_version = metadata.get('clusterVersion')
            configuration_versions = metadata.get('configurationVersions')
            dashboard_id = dashboard_json.get('id')
            dashboard_metadata = dashboard_json.get('dashboardMetadata')
            dashboard_name = dashboard_metadata.get('name')
            dashboard_owner = dashboard_metadata.get('owner')
            dashboard_shared = dashboard_metadata.get('shared')
            dashboard_preset = dashboard_metadata.get('preset')
            dashboard_popularity = dashboard_metadata.get('popularity')
            dashboard_tiles_name_size = dashboard_metadata.get('tilesNameSize')
            dashboard_has_consistent_colors = dashboard_metadata.get('hasConsistentColors')

            if cluster_version != current_cluster_version:
                fixes.append('ClusterVersion')
                dashboard_json['metadata']['clusterVersion'] = current_cluster_version

            if configuration_versions != current_configuration_versions:
                fixes.append('ConfigurationVersions')
                dashboard_json['metadata']['configurationVersions'] = current_configuration_versions

            if not dashboard_id.startswith('00000000-dddd-bbbb-ffff-00000000'):
                fixes.append('ID')
                # Assume there will be no more than 9 of these corrections per run!
                dashboard_json['id'] = f'00000000-dddd-bbbb-ffff-99999999000{id_index}'

            if not dashboard_name.startswith('TEMPLATE: '):
                fixes.append('Name')
                # Assume prefix is missing
                dashboard_json['dashboardMetadata']['name'] = f'TEMPLATE: {dashboard_name}'

            if dashboard_owner != 'nobody@example.com':
                fixes.append('Owner')
                dashboard_json['dashboardMetadata']['owner'] = 'nobody@example.com'

            if not dashboard_shared:
                fixes.append('Shared')
                dashboard_json['dashboardMetadata']['shared'] = True

            if dashboard_preset:
                fixes.append('Preset')
                dashboard_json['dashboardMetadata']['preset'] = False

            if dashboard_popularity:
                fixes.append('Popularity')
                dashboard_json['dashboardMetadata'].pop('popularity')

            if dashboard_tiles_name_size != 'small':
                fixes.append('TilesNameSize')
                dashboard_json['dashboardMetadata']['tilesNameSize'] = 'small'

            if not dashboard_has_consistent_colors:
                fixes.append('ConsistentColors')
                dashboard_json['dashboardMetadata']['hasConsistentColors'] = True

            if fixes:
                print(f'{dashboard_name}|{dashboard_id}|{dashboard_owner}| has bad {fixes}')

            # Now that different flavors are used, this cannot be done!
            # # Insure the ID is used for the dashboard file name
            # output_filename = f'{DASHBOARD_OUTPUT_PATH}/{dashboard_id}.json'

            output_filename = f'{DASHBOARD_OUTPUT_PATH}/{os.path.basename(filename)}'

            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(json.dumps(dashboard_json, indent=4, sort_keys=False))
        except JSONDecodeError:
            if filename not in file_skip_list:
                print(f'Skipping non-JSON file: {filename}')


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + DASHBOARD_OUTPUT_PATH + ' directory will now be removed to prepare for the conversion.')
        remove_directory(DASHBOARD_OUTPUT_PATH)

    if not os.path.isdir(DASHBOARD_OUTPUT_PATH):
        make_directory(DASHBOARD_OUTPUT_PATH)


def remove_directory(path):
    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def main():
    clean_dashboards()


if __name__ == '__main__':
    main()
