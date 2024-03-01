import copy
import json

INPUT_DASHBOARD__PATH = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000216.json'
OUTPUT_DASHBOARD_PATH = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000999.json'


def clone_dashboard():
    with open(INPUT_DASHBOARD__PATH, 'r', encoding='utf-8') as f:
        dashboard = f.read()
        new_dashboard = customize_dashboard(dashboard)
        name = new_dashboard.get('dashboardMetadata').get('name')
        new_dashboard['dashboardMetadata']['name'] = name + '-CUSTOMIZED'
        with open(OUTPUT_DASHBOARD_PATH, 'w', encoding='utf-8') as outfile:
            outfile.write(json.dumps(new_dashboard, indent=4, sort_keys=False))


def customize_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)

    new_tiles = []
    tiles = dashboard_json['tiles']
    for tile in tiles:
        if 'key user action' in str(tile):
            if 'custom action' not in str(tile):
                print(tile)
                new_tiles.append(tile)

    new_dashboard_json['tiles'] = new_tiles

    return new_dashboard_json


def main():
    clone_dashboard()


if __name__ == '__main__':
    main()
