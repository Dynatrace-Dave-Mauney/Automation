# Read all dashboards in the specified path and create an index with the specified file name.
#

import codecs
import glob
import json
import pathlib


def index_dashboards():
    file = pathlib.Path('Templates/Overview/dashboard_index.txt')
    outfile = codecs.open(str(file), 'w', encoding='utf-8')

    path = 'Templates/Overview/????????-????-????-????-????????????'
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = json.loads(f.read())
            dashboard_id = dashboard['id']
            dashboard_name = dashboard.get('dashboardMetadata').get('name')
            print(f'{dashboard_id}:{dashboard_name}', file=outfile)


def main():
    index_dashboards()


if __name__ == '__main__':
    main()
