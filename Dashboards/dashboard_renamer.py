import glob
import json
import os
import shutil
from inspect import currentframe

DASHBOARD_INPUT_PATH = '../$Input/Dashboards/Renamer'
DASHBOARD_OUTPUT_PATH = '../$Output/Dashboards/Renamed'

confirmation_required = True
remove_directory_at_startup = True


def rename_dashboards():
    confirm('Rename dashboards from ' + DASHBOARD_INPUT_PATH + ' to ' + DASHBOARD_OUTPUT_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_INPUT_PATH + '/*'):
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            name = dashboard_json.get('dashboardMetadata').get('name')
            new_name = normalize(name)
            output_filename = DASHBOARD_OUTPUT_PATH + '/' + new_name
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(dashboard)


def normalize(name):
    new_name = name
    new_name = new_name.replace('TEMPLATE: ', '')
    new_name = new_name.replace(' - ', '_')
    new_name = new_name.replace(' ', '_')
    new_name = new_name.replace(':', '_')
    print(name + ' -> ' + new_name)
    return new_name


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
    rename_dashboards()


if __name__ == '__main__':
    main()
