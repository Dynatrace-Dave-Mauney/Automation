import glob
import json
import os
from json import JSONDecodeError

current_cluster_version = '1.261.134.20230302-084304'
current_configuration_versions = [6]

DASHBOARD_INPUT_PATH = 'Templates/Overview'
# DASHBOARD_INPUT_PATH = 'Templates-Overview-Clean'


def verify_dashboards():
    for filename in glob.glob(DASHBOARD_INPUT_PATH + '/*'):
        if os.path.isfile(filename):
            verify_dashboard(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_directory(path):
    for filename in glob.glob(path + '/*'):
        if os.path.isfile(filename):
            verify_dashboard(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def verify_dashboard(filename):
    # print(f'Processing {filename}')

    violations = []

    if not filename.endswith(".json"):
        return

    if "markdown_" in filename:
        return

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
                violations.append('ClusterVersion')

            if configuration_versions != current_configuration_versions:
                violations.append('ConfigurationVersions')

            if not dashboard_id.startswith('00000000-dddd-bbbb-ffff-00000000'):
                violations.append('ID')

            if not dashboard_name.startswith('TEMPLATE: '):
                violations.append('Name')

            if dashboard_owner != 'nobody@example.com':
                violations.append('Owner')

            if not dashboard_shared:
                violations.append('Shared')

            if dashboard_preset:
                violations.append('Preset')

            if dashboard_popularity:
                violations.append('Popularity')

            if dashboard_tiles_name_size != 'small':
                violations.append('TilesNameSize')

            if not dashboard_has_consistent_colors:
                violations.append('ConsistentColors')

            no_back_to_overview_expected_list = [
                '00000000-dddd-bbbb-ffff-000000000001',
            ]
            if not "Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001" in dashboard:
                if dashboard_id not in no_back_to_overview_expected_list:
                    violations.append('No "Back to Overview" markdown tile')

            if violations:
                print(f'{dashboard_name}|{dashboard_id}|{dashboard_owner}| has violations: {violations}')

        except JSONDecodeError:
            print(f'Skipping file because the contents are not parseable JSON: {filename}')


def main():
    verify_dashboards()


if __name__ == '__main__':
    main()
