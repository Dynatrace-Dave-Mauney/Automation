import copy
import glob
import json
import os

def list_metrics():
    dashboard_filename = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000079.json'
    dashboard_filename = '/Temp/F5 Metrics Curated.json'
    for filename in glob.glob(dashboard_filename):
        with open(filename, 'r', encoding='utf-8') as f:
            print(filename)
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            for tile in dashboard_json.get('tiles'):
                tile_name = tile.get('customName')
                tile_query = tile.get('queries')[0].get('metric')
                print(f'{tile_name}: {tile_query}')

def main():
    list_metrics()


if __name__ == '__main__':
    main()
