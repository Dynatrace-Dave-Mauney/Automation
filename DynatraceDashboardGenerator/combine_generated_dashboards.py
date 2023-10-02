#
# When dashboards are generated for different tenants, combine the best ones by selecting the
# dashboards that have the largest number of tiles.
#

import glob
import json
import os
import shutil
from json import JSONDecodeError

LEFT_GLOB_PATH = 'aaaaaaaa-bbbb-cccc-dddd-*'
RIGHT_GLOB_PATH = 'bbbbbbbb-bbbb-cccc-dddd-*'
OUTPUT_PATH = 'Combined'
OUTPUT_PREFIX = '0000aaaa-bbbb-cccc-dddd-'

confirmation_required = True
remove_directory_at_startup = True


def process():
    confirm(f'Combine generated dashboards from {LEFT_GLOB_PATH} and {RIGHT_GLOB_PATH} to {OUTPUT_PATH}')
    initialize()

    left_dict = load_dict(LEFT_GLOB_PATH)
    right_dict = load_dict(RIGHT_GLOB_PATH)
    select_dashboards(left_dict, right_dict)


def load_dict(glob_path):
    dashboard_dict = {}
    for filename in glob.glob(glob_path):
        if os.path.isfile(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                infile_content = f.read()
                try:
                    infile_content_json = json.loads(infile_content)
                    dashboard_name = infile_content_json.get('dashboardMetadata').get('name')
                    dashboard_tile_count = len(infile_content_json.get('tiles'))
                    dashboard_dict[dashboard_name] = {'tiles': dashboard_tile_count, 'content': infile_content_json}
                except JSONDecodeError:
                    print(f'Skipping due to non-JSON file content: {filename}')

    return dashboard_dict


def select_dashboards(left_dict, right_dict):
    selected_dashboard_dicts = []
    left_keys = left_dict.keys()
    right_keys = right_dict.keys()
    all_keys = left_keys | right_keys
    for key in all_keys:
        try:
            left_item = left_dict[key]
            left_tile_count = left_item.get('tiles')
        except KeyError:
            left_item = None
            left_tile_count = 0
        try:
            right_item = right_dict[key]
            right_tile_count = right_item.get('tiles')
        except KeyError:
            right_item = None
            right_tile_count = 0
        # print(f'{key}: {left_tile_count},{right_tile_count}')
        if left_tile_count >= right_tile_count:
            left_item['name'] = key
            selected_dashboard_dicts.append(left_item)
        else:
            right_item['name'] = key
            selected_dashboard_dicts.append(right_item)

    dashboard_counter = 1
    for selected_dashboard_dict in sorted(selected_dashboard_dicts, key=lambda x: x['name']):
        dashboard = selected_dashboard_dict.get('content')
        # print(dashboard)
        new_dashboard_id = f"{OUTPUT_PREFIX}{format(dashboard_counter, '012d')}"
        dashboard_counter += 1
        dashboard['id'] = new_dashboard_id
        output_filename = os.path.join(OUTPUT_PATH, f'{new_dashboard_id}.json')

        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(dashboard, indent=4, sort_keys=False))


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + OUTPUT_PATH + ' directory will now be removed.')
        remove_directory(OUTPUT_PATH)

    if not os.path.isdir(OUTPUT_PATH):
        make_directory(OUTPUT_PATH)


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
            print('Operation aborted')
            exit()


def main():
    process()


if __name__ == '__main__':
    main()
