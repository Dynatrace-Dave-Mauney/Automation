import os
import glob
import json
import re


def main():
    selected_count = 0
    try:
        input_glob_pattern = "../../AI/Copilot/Dashboards/Generation/generated_gen3/*.json"

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.json') and not file_name.endswith('.metadata.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    dashboard_tiles = input_json.get('tiles')
                    for dashboard_tile_key in dashboard_tiles.keys():
                        dashboard_tile = dashboard_tiles[dashboard_tile_key]
                        dashboard_tile_query = dashboard_tile.get('query')
                        if dashboard_tile_query:
                            dashboard_name = re.sub('.*\\\\TEMPLATE - ', '', file_name).replace('.json', '')
                            metric, by, fields_add = get_query_parts(dashboard_tile_query)
                            if not by:
                                if not fields_add:
                                    print(f'Missing by/fieldsAdd: metric: "{metric}" dashboard: {dashboard_name}')
                                else:
                                    print(f'Missing by: metric: "{metric}", fieldsAdd: {fields_add} dashboard: {dashboard_name}')
                            else:
                                if not fields_add:
                                    print(f'Missing fieldsAdd: metric: "{metric}", by: {by} dashboard: {dashboard_name}')

                        # if 'fieldsAdd' not in dashboard_tile_query:
                        #     print(dashboard_tile_query)
                        #     selected_count += 1
    except FileNotFoundError:
        print('The directory name does not exist')

    print(f'Total Selected: {selected_count}')


def get_query_parts(query):
    metric = re.sub('timeseries.*\(', '', query)
    metric = re.sub('\).*', '', metric, flags=re.DOTALL)
    metric = re.sub(',.*', '', metric, flags=re.DOTALL)

    by = None
    if 'by' in query:
        by = re.sub('.*by:', '', query, flags=re.DOTALL)
        by = re.sub('}.*', '', by, flags=re.DOTALL)
        by = re.sub(',.*', '', by, flags=re.DOTALL)
        by = re.sub('\{', '', by, flags=re.DOTALL)
        by = re.sub('\|.*', '', by, flags=re.DOTALL)
        # remove all whitespace
        by = re.sub(r'\s+', '', by, flags=re.DOTALL)
        # print('by:', by)

    fields_add = None
    if 'fieldsAdd' in query:
        # print('query:', query)
        fields_add = re.sub('.*fieldsAdd', '', query, flags=re.DOTALL)
        fields_add = re.sub('\|.*', '', fields_add, flags=re.DOTALL)
        fields_add = re.sub(',.*', '', fields_add, flags=re.DOTALL)
        fields_add = re.sub('\)', ')', fields_add, flags=re.DOTALL)
        # remove all whitespace
        fields_add = re.sub(r'\s+', '', fields_add, flags=re.DOTALL)
        # re.sub(r'\s+', '', text)
        # print('fields_add:', fields_add)

    return metric, by, fields_add


if __name__ == '__main__':
    main()
