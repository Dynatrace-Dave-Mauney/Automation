import copy
import glob
import json
import os
import re
import shutil
from inspect import currentframe
from pathlib import Path

DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'
DASHBOARD_FIXED_PATH = 'Templates-Overview-Splits'


def fix_dashboards():
    # confirm('fix dashboards from ' + DASHBOARD_TEMPLATE_PATH + ' to ' + DASHBOARD_FIXED_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_TEMPLATE_PATH + '/00000000-*'):
        base_name = Path(filename).name

        fix_list = [
            '00000000-dddd-bbbb-ffff-000000000182.json',
            '00000000-dddd-bbbb-ffff-000000000195.json',
            '00000000-dddd-bbbb-ffff-000000000196.json',
            '00000000-dddd-bbbb-ffff-000000000821.json',
            '00000000-dddd-bbbb-ffff-000000000823.json',
            '00000000-dddd-bbbb-ffff-000000000824.json',
            '00000000-dddd-bbbb-ffff-000000000825.json',
            '00000000-dddd-bbbb-ffff-000000000826.json',
            '00000000-dddd-bbbb-ffff-000000001011.json',
            '00000000-dddd-bbbb-ffff-000000001026.json',
            '00000000-dddd-bbbb-ffff-000000001027.json',
            '00000000-dddd-bbbb-ffff-000000001032.json',
            '00000000-dddd-bbbb-ffff-000000001103.json',
        ]

        if base_name not in fix_list:
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            new_dashboard = fix_dashboard(dashboard)
            pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
            # name = new_dashboard.get('dashboardMetadata').get('name')
            output_filename = DASHBOARD_FIXED_PATH + '/' + os.path.basename(filename)
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(pretty_new_dashboard)


def fix_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    name = dashboard_json.get('dashboardMetadata').get('name')

    tiles = new_dashboard_json.get('tiles')

    # print('dashboard name:', name)
    for tile in tiles:
        tile_type = tile.get('tileType')
        # print('tile_type:', tile_type)
        if tile_type != 'DATA_EXPLORER':
            continue

        tile_name = tile.get('name')
        tile_custom_name = tile.get('customName')
        tile_queries = tile.get('queries')
        tile_queries_split_by = []
        if tile_queries:
            tile_queries_split_by = tile_queries[0].get('splitBy', [])
        tile_metric_expressions = tile.get('metricExpressions')
        tile_metric_expressions_split_by = ''
        if tile_metric_expressions and len(tile_metric_expressions) > 0:
            tile_metric_expressions_split_by = re.match(r"splitBy(.*)", tile_metric_expressions[0])
            if not tile_metric_expressions_split_by:
                tile_metric_expressions_split_by = ''

        # print(tile_name, tile_custom_name, tile_queries_split_by, str(tile_queries[0]), str(tile_metric_expressions[0]))
        # print(tile_name, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)

        if not tile_custom_name:
            tile_custom_name = tile_name

        if 'Cohesity' in name:
            fix_cohesity(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
        else:
            if 'NAS Storage' in name:
                fix_nas_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
            else:
                if 'SAN Storage' in name:
                    fix_san_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
                else:
                    if 'Self-Monitoring' in name:
                        fix_self_monitoring(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
                    else:
                        if 'AWS' in name:
                            fix_aws(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)

    return new_dashboard_json


def fix_cohesity(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING Cohesity...')

    new_split = None

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        if 'alert' in tile_custom_name:
            new_split = 'alert_name'
        else:
            if 'job' in tile_custom_name:
                new_split = 'job_name'
            else:
                if 'cluster' in tile_custom_name:
                    new_split = 'cluster_name'
                else:
                    if 'node' in tile_custom_name:
                        new_split = 'node_name'

        print(tile_custom_name, new_split)

        if new_split:
            tile['queries'][0]['splitBy'] = [new_split]
            tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_nas_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING NAS Storage...')

    new_split = None

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        if 'alert' in tile_custom_name:
            new_split = 'nas.alert_summary'
        else:
            if 'array' in tile_custom_name:
                new_split = 'nas.source_array'
            else:
                if 'account' in tile_custom_name:
                    new_split = 'nas.account_name'
                else:
                    if 'bucket' in tile_custom_name:
                        new_split = 'nas.bucket_name'
                    else:
                        if 'hardware' in tile_custom_name or 'file_system' in tile_custom_name:
                            new_split = 'nas.component_name'

        print(tile_custom_name, new_split)

        if new_split:
            tile['queries'][0]['splitBy'] = [new_split]
            tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_san_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING SAN Storage...')

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        new_split = 'san.array_name'

        print(tile_custom_name, new_split)

        tile['queries'][0]['splitBy'] = [new_split]
        tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_self_monitoring(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING Self Monitoring...')

    tile_queries = tile.get('queries')[0]
    tile_queries_metric = tile_queries.get('metric')
    print('tile_queries_metric:', tile_queries_metric)

    new_split = None

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        if 'active_gate' in tile_queries_metric:
            new_split = 'host.name'
        else:
            if 'extension.engine' in tile_queries_metric:
                new_split = 'host.name'
            else:
                if 'extension' in tile_queries_metric:
                    new_split = 'dt.extension.name'
                else:
                    if 'datasource.wmi' in tile_queries_metric:
                        new_split = 'host.name'
                    else:
                        # For all non-wmi data sources
                        if 'datasource' in tile_queries_metric:
                            new_split = 'dt.metrics.source'
                        else:
                            if 'agent_modules' in tile_queries_metric:
                                new_split = 'dt.oneagent.health_state'
                            else:
                                if 'storage' in tile_queries_metric:
                                    new_split = 'data.type'
                                else:
                                    if 'synthetic' in tile_queries_metric:
                                        new_split = 'dt.entity.synthetic_location'

        print(tile_custom_name, tile_queries_metric, new_split)

        if new_split:
            tile['queries'][0]['splitBy'] = [new_split]
            tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_aws(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    print('FIXING AWS...')

    tile_queries = tile.get('queries')[0]
    tile_queries_metric = tile_queries.get('metric')
    print('tile_queries_metric:', tile_queries_metric)

    new_split = None

    if tile_queries_metric.endswith('ByRegion'):
        new_split = 'Region'
    else:
        if tile_queries_metric.endswith('ByRegionEngineName'):
            new_split = 'Region,EngineName'
        else:
            if tile_queries_metric.endswith('ByRegionHost'):
                new_split = 'Region,Host'
            else:
                if tile_queries_metric.endswith('ByRegionRule'):
                    new_split = 'Region,Rule'
                else:
                    if tile_queries_metric.endswith('ByRegionOperation'):
                        new_split = 'Region,Operation'
                    else:
                        if tile_queries_metric.endswith('ByMetricGroupQueueName'):
                            new_split = 'MetricGroup,QueueName'
                        else:
                            if 'aws.az' in tile_queries_metric:
                                new_split = 'dt.entity.aws_availability_zone'
                            else:
                                if 'aws.connect.contactFlow' in tile_queries_metric:
                                    new_split = 'ContactFlowName'

        print(tile_custom_name, tile_queries_metric, new_split)

        if new_split:
            new_split_list = to_list(new_split)
            tile['queries'][0]['splitBy'] = new_split_list
            if tile.get('metricExpressions'):
                tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def to_list(new_split):
    if ',' in new_split:
        return new_split.split(',')
    else:
        return [new_split]


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
