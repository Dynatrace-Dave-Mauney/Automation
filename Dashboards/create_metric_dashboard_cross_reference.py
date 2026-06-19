import glob
import json
import os

from pathlib import Path

DASHBOARD_CLASSIC_INPUT_PATH = 'Templates/Overview'
DASHBOARD_GEN3_INPUT_PATH = '../NewPlatform/Dashboards/Assets'

cross_reference_list = []

def create_metric_dashboard_cross_reference(path):
    for filename in glob.glob(path + '/*'):
        if os.path.isfile(filename):
            process_dashboard(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_directory(path):
    for filename in glob.glob(path + '/*'):
        if os.path.isfile(filename):
            process_dashboard(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_dashboard(filename):
    global cross_reference_list

    file_path = Path(filename)
    if file_path.match('00000000-dddd-bbbb-ffff-00000000????.json'):
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            dashboard_id = dashboard_json.get('id')
            dashboard_metadata = dashboard_json.get('dashboardMetadata')
            dashboard_name = dashboard_metadata.get('name').replace('TEMPLATE', 'Prod')
            dashboard_tiles = dashboard_json.get('tiles')

            for dashboard_tile in dashboard_tiles:
                dashboard_tile_queries = dashboard_tile.get('queries')
                if dashboard_tile_queries:
                    dashboard_tile_queries_metric = dashboard_tile_queries[0].get('metric')
                    if dashboard_tile_queries_metric:
                        dashboard_tile_name = dashboard_tile.get('name')
                        # print(dashboard_tile_queries_metric, dashboard_name, dashboard_id)
                        cross_reference_list.append([dashboard_tile_queries_metric, dashboard_tile_name, dashboard_name, dashboard_id])

if __name__ == '__main__':
    # create_metric_dashboard_cross_reference(DASHBOARD_CLASSIC_INPUT_PATH)
    create_metric_dashboard_cross_reference(DASHBOARD_GEN3_INPUT_PATH)

    for cross_reference_list_item in sorted(cross_reference_list):
        print(cross_reference_list_item)


