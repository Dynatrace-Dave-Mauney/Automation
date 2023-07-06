# Read all generated dashboards in the current directory and create an index.
#
# CAUTION:
#
# The file name is assumed to be the dashboard id.
# All files in the current directory with the following format will be assumed to be dashboards:
# ????????-????-????-????-????????????.json
# Example:
# aaaaaaaa-bbbb-cccc-dddd-000000000001.json
#

import glob
import json
import pathlib

def index_dashboards():
    file = pathlib.Path('dashboard_index.txt')
    outfile = open(str(file), 'w')

    path = './????????-????-????-????-????????????.json'
    for filename in glob.glob(path):
        # print(filename)
        with open(filename, 'r') as f:
            try:
                dashboard_id = filename.replace('.json', '').replace('.\\', '')
                print(dashboard_id + ':' + json.loads(f.read())['dashboardMetadata']['name'], file=outfile)
            except KeyError:
                print(f'Skipping {dashboard_id} due to missing "dashboardMetadata"')

def main() -> object:
   index_dashboards()


if __name__ == '__main__':
    main()
