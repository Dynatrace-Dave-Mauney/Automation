import os
import glob
import json


def main():
    selected_count = 0
    try:
        input_glob_pattern = "../../Dashboards/Templates/Overview/0*.json"

        dashboard_tile_types = []
        dashboard_tile_visual_config_types = []

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    dashboard_metadata = input_json.get('dashboardMetadata')
                    if dashboard_metadata:
                        dashboard_name = dashboard_metadata.get('name')
                        dashboard_id = input_json.get('id')
                        print(dashboard_id, dashboard_name)
                        dashboard_tiles = input_json.get('tiles')
                        for dashboard_tile in dashboard_tiles:
                            dashboard_tile_type = dashboard_tile.get('tileType')
                            print(dashboard_tile_type)
                            # if dashboard_tile_type == 'DTAQL':
                            #     print(dashboard_id, dashboard_tile_type)

                            if dashboard_tile_type == 'DATA_EXPLORER':
                                visual_config_type = dashboard_tile.get('visualConfig', {}).get('type')
                                if visual_config_type and visual_config_type not in dashboard_tile_visual_config_types:
                                    dashboard_tile_visual_config_types.append(visual_config_type)

                            if dashboard_tile_type not in dashboard_tile_types:
                                dashboard_tile_types.append(dashboard_tile_type)
                        selected_count += 1
    except FileNotFoundError:
        print('The directory name does not exist')

    print('Dashboard Tile Types:')
    for dashboard_tile_type in sorted(dashboard_tile_types):
        print(dashboard_tile_type)

    print('Dashboard Visual Config Tile Types:')
    for dashboard_tile_visual_config_type in sorted(dashboard_tile_visual_config_types):
        print(dashboard_tile_visual_config_type)

    print(f'Total Selected: {selected_count}')


if __name__ == '__main__':
    main()
