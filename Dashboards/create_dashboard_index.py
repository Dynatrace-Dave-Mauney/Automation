# Read all dashboards in the specified path and create an index by id and by name with the specified file names.
#

import codecs
import glob
import json
import pathlib


def index_dashboards(path, index_by_id_file, index_by_name_file):
    print(f'index_dashboards({path}, {index_by_id_file}, {index_by_name_file})')
    if not index_by_id_file and not index_by_name_file:
        print('Nothing to do!  Specify at least one file name!')
        exit()

    lines_by_id = []
    lines_by_name = []

    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = json.loads(f.read())
            dashboard_id = dashboard.get('id')
            dashboard_metadata = dashboard.get('dashboardMetadata')
            if dashboard_metadata:
                dashboard_name = dashboard_metadata.get('name')
                lines_by_id.append(f'{dashboard_id}|{dashboard_name}')
                lines_by_name.append(f'{dashboard_name}|{dashboard_id}')

    if index_by_id_file:
        index_by_id_outfile = codecs.open(str(index_by_id_file), 'w', encoding='utf-8')
        for line in sorted(lines_by_id):
            print(line, file=index_by_id_outfile)

    if index_by_name_file:
        index_by_name_outfile = codecs.open(str(index_by_name_file), 'w', encoding='utf-8')
        for line in sorted(lines_by_name):
            print(line, file=index_by_name_outfile)


def main():
    path = 'Templates/Overview/????????-????-????-????-????????????.json'
    index_by_id_file = pathlib.Path('Templates/Overview/dashboard_index_by_id.txt')
    index_by_name_file = pathlib.Path('Templates/Overview/dashboard_index_by_name.txt')
    index_dashboards(path, index_by_id_file, index_by_name_file)

    path = 'Sandbox/????????-????-????-????-????????????.json'
    index_by_id_file = pathlib.Path('Sandbox/dashboard_index_by_id.txt')
    index_by_name_file = pathlib.Path('Sandbox/dashboard_index_by_name.txt')
    index_dashboards(path, index_by_id_file, index_by_name_file)

    path = '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000???.json'
    index_by_id_file = pathlib.Path('../DynatraceDashboardGenerator/dashboard_index_by_id.txt')
    index_by_name_file = pathlib.Path('../DynatraceDashboardGenerator/dashboard_index_by_name.txt')
    index_dashboards(path, index_by_id_file, index_by_name_file)


if __name__ == '__main__':
    main()
