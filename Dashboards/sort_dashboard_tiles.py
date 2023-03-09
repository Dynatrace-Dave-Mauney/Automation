import copy
import glob
import json
import os
import shutil
from inspect import currentframe

# DASHBOARD_INPUT_PATH = '../$Input/Dashboards/Examples'
# DASHBOARD_OUTPUT_PATH = '../$Output/Dashboards/Sorted'

DASHBOARD_INPUT_PATH = 'Templates-Overview-Clean'
DASHBOARD_OUTPUT_PATH = 'Templates-Overview-Clean-Sorted'

# DASHBOARD_INPUT_PATH = 'Templates-Overview-Clean-Sorted'
# DASHBOARD_OUTPUT_PATH = 'Templates-Overview-Clean-Resorted'

confirmation_required = True
remove_directory_at_startup = True


def sort_dashboards():
    confirm('Sort dashboards from ' + DASHBOARD_INPUT_PATH + ' to ' + DASHBOARD_OUTPUT_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_INPUT_PATH + '/*'):
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            new_dashboard = sort_dashboard_tiles(dashboard)
            pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
            if pretty_new_dashboard != dashboard:
                print(f'Modified {filename}')
            output_filename = DASHBOARD_OUTPUT_PATH + '/' + os.path.basename(filename)
            with open(output_filename, 'w') as outfile:
                outfile.write(pretty_new_dashboard)


def sort_dashboard_tiles(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    tiles = new_dashboard_json.get('tiles')
    sorted_tiles = sorted(tiles, key=lambda k: (k['bounds']['top'], k['bounds']['left']))
    new_dashboard_json['tiles'] = sorted_tiles
    return new_dashboard_json


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
    sort_dashboards()


if __name__ == '__main__':
    main()
