import copy
import glob
import json
import os
import shutil
from inspect import currentframe

DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'
DASHBOARD_FIXED_PATH = 'Templates/Overview-WithReturnFix'

return_to_overview_markdown_tile = {
            "name": "Markdown",
            "tileType": "MARKDOWN",
            "configured": True,
            "bounds": {
                "top": 0,
                "left": 1368,
                "width": 152,
                "height": 38
            },
            "tileFilter": {},
            "markdown": "## [\u21e6 Return to Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\n![BackButton]()"
        }

return_to_overview_markdown_string = "## [\u21e6 Return to Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\n![BackButton]()"

dashboard_metadata_template = {
        "name": None,
        "shared": True,
        "owner": "nobody@example.com",
        "dashboardFilter": None,
        "preset": True,
        "tilesNameSize": "small",
        "hasConsistentColors": True}


def fix_dashboards():
    # confirm('fix dashboards from ' + DASHBOARD_TEMPLATE_PATH + ' to ' + DASHBOARD_FIXED_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_TEMPLATE_PATH + '/00000000-*'):
        # print(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            new_dashboard = fix_dashboard(dashboard)
            pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
            name = new_dashboard.get('dashboardMetadata').get('name')
            output_filename = DASHBOARD_FIXED_PATH + '/' + os.path.basename(filename)
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(pretty_new_dashboard)


def fix_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    name = dashboard_json.get('dashboardMetadata').get('name')

    new_dashboard_json['dashboardMetadata'] = dashboard_metadata_template
    new_dashboard_json['dashboardMetadata']['name'] = name

    # Use as needed for verification purposes...
    # if not verify_dashboard_metadata(new_dashboard_json):
    #     print(f'Bad metadata for "{name}":')
    #     print(str(new_dashboard_json.get('dashboardMetadata')))
    #     exit(1234)

    tiles = new_dashboard_json.get('tiles')

    left = get_left(tiles)

    # print(f'{name} left is {left}')
    if 'TEMPLATE: Overview' not in name:
        if '⇦' not in str(dashboard):
            tiles = new_dashboard_json.get('tiles')
            return_to_overview_markdown_tile['bounds']['left'] = left
            tiles.append(return_to_overview_markdown_tile)
            new_dashboard_json['tiles'] = tiles
            print(f'Added a "Return to Overview" tile to {name} at {left}')
        else:
            index = 0
            for tile in new_dashboard_json.get('tiles'):
                if '⇦' in str(tile) and 'Return to Overview' not in str(tile):
                    new_markdown = tile.get('markdown').replace('⇦', '⇦ Return to Overview')
                    new_dashboard_json['tiles'][index] = new_markdown
                    print(f'Added "Return to Overview" string to the existing tile in {name}')
                index += 1

    return new_dashboard_json

def verify_dashboard_metadata(dashboard):
    dashboard_metadata = dashboard.get('dashboardMetadata')
    shared = dashboard_metadata.get('shared')
    owner = dashboard_metadata.get('owner')
    dashboard_filter = dashboard_metadata.get('dashboardFilter')
    preset = dashboard_metadata.get('preset')
    tiles_name_size = dashboard_metadata.get('tilesNameSize')
    has_consistent_colors = dashboard_metadata.get('hasConsistentColors')

    if not shared:
        print(f'shared: {shared}')
        return False

    if not preset:
        print(f'preset: {preset}')
        return False

    if owner != 'nobody@example.com':
        print(f'owner: {owner}')
        return False

    if dashboard_filter != None:
        print(f'dashboard_filter: {dashboard_filter}')
        return False

    if tiles_name_size != 'small':
        print(f'tiles_name_size: {tiles_name_size}')
        return False

    if not has_consistent_colors:
        print(f'has_consistent_colors: {has_consistent_colors}')
        return False

    return True


def get_left(tiles):
    max_left = 0
    for tile in tiles:
        if '⇦' not in str(tile):
            bounds = tile.get('bounds')
            left = bounds.get('left')
            width = bounds.get('width')
            next_left = int(left) + int(width)
            if next_left > max_left:
                max_left = next_left

    if max_left < 1368:
        max_left = 1368

    return max_left

def initialize():
    # confirm('The ' + DASHBOARD_FIXED_PATH + ' directory will now be removed to prepare for the conversion.')
    remove_directory(DASHBOARD_FIXED_PATH)

    if not os.path.isdir(DASHBOARD_FIXED_PATH):
        make_directory(DASHBOARD_FIXED_PATH)


def remove_directory(path):
    print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    print('confirm(' + message + ')')
    proceed = input('%s (Y/n) ' % message).upper() == 'Y'
    if not proceed:
        exit(get_linenumber())


def get_linenumber():
    print('get_linenumber()')
    cf = currentframe()
    return cf.f_back.f_lineno


def main():
    fix_dashboards()


if __name__ == '__main__':
    main()
