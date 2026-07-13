import os
import glob
import json
import re


def main():
    selected_count = 0
    try:
        input_glob_pattern = "../../Dashboards/Templates/Overview/0*.json"

        encountered_names = []

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.json') and '-v' not in file_name:
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    dashboard_metadata = input_json.get('dashboardMetadata')
                    if dashboard_metadata:
                        dashboard_name = dashboard_metadata.get('name')

                        if dashboard_name in encountered_names:
                            dashboard_id = input_json.get('id')
                            print('Duplicate name:', dashboard_name, dashboard_id)
                        else:
                            encountered_names.append(dashboard_name)
                            selected_count += 1
    except FileNotFoundError:
        print('The directory name does not exist')

    print(f'Total Selected: {selected_count}')


if __name__ == '__main__':
    main()
