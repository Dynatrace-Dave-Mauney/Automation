# Note: Be sure to change columns_per_row, if needed.

import copy
import glob
import json
import os

DASHBOARD_INPUT_PATH = '/Temp/MSHS/NewPlatform/Dashboards/Pure*json'
DASHBOARD_OUTPUT_PATH = '/Temp/MSHS/NewPlatform/Dashboards-Layout-Changed'


def process_dashboards():
    for filename in glob.glob(DASHBOARD_INPUT_PATH):
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = json.loads(f.read())
            new_dashboard = convert_dashboard(dashboard)
            basename = os.path.basename(filename)
            output_filename = DASHBOARD_OUTPUT_PATH + '/' + basename
            print(f'Converting {filename} to {output_filename}')
            with open(output_filename, 'w') as outfile:
                outfile.write(json.dumps(new_dashboard, indent=4, sort_keys=False))


def convert_dashboard(dashboard):
    new_dashboard_json = copy.deepcopy(dashboard)

    tile_count = len(new_dashboard_json.get('layouts'))
    new_dashboard_layout = configure_layout(tile_count)
    new_dashboard_json['layouts'] = new_dashboard_layout
    # new_dashboard_json['settings'] = {}
    # new_dashboard_json['settings']['gridLayout']['columnsCount'] = 3
    new_dashboard_json['settings']['gridLayout']['mode'] = 'responsive'
    new_dashboard_json['importedWithCode'] = False
    return new_dashboard_json


def configure_layout(tile_count):
    # Choose how many columns per row and the rest is magic
    columns_per_row = 3

    layouts = {}
    index = 0

    x = 0
    y = 0
    # w = 16
    w = 48 / columns_per_row
    h = 8

    while index < tile_count:
        key = str(index)
        layouts[key] = {"x": x, "y": y, "w": w, "h": h}
        x += w
        index += 1

        # When max columns reached per row
        if x == w * columns_per_row:
            x = 0
            y += h

    return layouts


def main():
    process_dashboards()


if __name__ == '__main__':
    main()
