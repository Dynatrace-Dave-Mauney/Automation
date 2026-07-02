import os
import glob
import json


def main():
    selected_count = 0
    try:
        input_glob_pattern = "../../Dashboards/Templates/Overview/0*.json"

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    dashboard_metadata = input_json.get('dashboardMetadata')
                    if dashboard_metadata:
                        dashboard_name = dashboard_metadata.get('name')
                        dashboard_id = input_json.get('id')
                        dashboard_tiles = input_json.get('tiles')
                        for dashboard_tile in dashboard_tiles:
                            dashboard_tile_type = dashboard_tile.get('tileType')
                            if dashboard_tile_type == 'DATA_EXPLORER':
                                dashboard_tile_name = dashboard_tile.get('name')
                                dashboard_tile_custom_name = dashboard_tile.get('customName')
                                if dashboard_tile_custom_name == 'Data explorer results' and dashboard_tile_name != dashboard_tile_custom_name:
                                    print(dashboard_id, dashboard_name, dashboard_tile_name, dashboard_tile_custom_name)
                                    selected_count += 1
    except FileNotFoundError:
        print('The directory name does not exist')

    print(f'Total Selected: {selected_count}')


if __name__ == '__main__':
    main()
