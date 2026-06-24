#
# Convert each Dynatrace classic dashboard to a new dashboard.
#
# USQL Tile not handled yet:
# Tenant1: 3rd Party XHR Detection
# https://eqh47714.live.dynatrace.com/#edit;gtf=-365d%20to%20now;gf=all;id=00000000-dddd-bbbb-ffff-000000000808

import copy
import glob
import json
import re

from Reuse import environment

DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-00000000????.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000000008.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000000009.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000000011.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000000808.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000001102.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000000192.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-000000000008.json'
# DASHBOARD_INPUT_PATH = '../../Dashboards/Custom/Overview-Tenant1/00000000-dddd-bbbb-ffff-00000000????*.json'
# DASHBOARD_INPUT_PATH = '../../$Private/Input/Dashboards/ClassicConversion/*'
DASHBOARD_OUTPUT_PATH = '../../$Private/$Output/Dashboards/ClassicConversion'

DASHBOARD_TEMPLATE_FILE_NAME = 'dashboard_template_dql.json'

# Global Variable read from YAML
classic_metric_to_grail_metric_dict = {}


def convert_dashboards():
    dashboard_template = get_dashboard_template()

    for filename in glob.glob(DASHBOARD_INPUT_PATH):
        # print(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = json.loads(f.read())
            new_dashboard = convert_dashboard(dashboard, dashboard_template)
            dashboard_id = dashboard.get('id')

            # if dashboard_id == '00000000-dddd-bbbb-ffff-000000000025.json':
            #     continue

            # cherry pick the most important dashboards
            # if dashboard_id not in [
            #     '00000000-dddd-bbbb-ffff-000000000001',
            #     '00000000-dddd-bbbb-ffff-000000000004',
            #     '00000000-dddd-bbbb-ffff-000000000005',
            #     '00000000-dddd-bbbb-ffff-000000000006',
            #     '00000000-dddd-bbbb-ffff-000000000007',
            #     '00000000-dddd-bbbb-ffff-000000000008',
            # ]:
            #     continue

            dashboard_name = dashboard.get('dashboardMetadata').get('name')

            # if dashboard_name not in [
            #     'Tenant1: Application Overview (HTTP Monitors and Services)',
            #     'Tenant1: Application Overview (Services)',
            #     'Tenant1: Application Overview (Synthetics and Services)',
            #     'Tenant1: Application Overview (Web, HTTP Monitors, and Services)',
            #     'Tenant1: Application Overview (Web, Synthetics, and Services)',
            #     'Tenant1: Backend Overview',
            #     'Tenant1: Containers',
            #     'Tenant1: DPS Usage Details',
            #     'Tenant1: Full Stack Overview',
            #     'Tenant1: Go',
            #     'Tenant1: Host Health Breakdown',
            #     'Tenant1: Hosts (Detailed)',
            #     'Tenant1: Hosts',
            #     'Tenant1: Java Memory',
            #     'Tenant1: Java Monitoring',
            #     'Tenant1: Kubernetes Overview',
            #     'Tenant1: Monitoring Overview',
            #     'Tenant1: Network (Host-Level Details)',
            #     'Tenant1: Network (Process-Level Details)',
            #     'Tenant1: Node.js',
            #     'Tenant1: Overview',
            #     'Tenant1: Service Errors',
            #     'Tenant1: Service HTTP Errors',
            #     'Tenant1: Services',
            #     'Tenant1: Synthetics HTTP Monitors',
            #     'Tenant1: VMware',
            #     'Tenant1: Web Servers',
            # ]:
            #     print(f'Skipping dashboard: "{dashboard_name}"')
            #     continue

            # if dashboard_name not in [
            #     'TEMPLATE: Hosts',
            # ]:
            #     print(f'Skipping dashboard: "{dashboard_name}"')
            #     continue

            # Write new dashboard if there are tiles
            if new_dashboard.get('tiles'):
                clean_dashboard_name = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "", dashboard_name)
                output_filename = DASHBOARD_OUTPUT_PATH + '/' + clean_dashboard_name + '.json'
                print(f'Converting {filename} to {output_filename}')
                with open(output_filename, 'w') as outfile:
                    outfile.write(json.dumps(new_dashboard, indent=4, sort_keys=False))
            else:
                clean_dashboard_name = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "", dashboard_name)
                output_filename = DASHBOARD_OUTPUT_PATH + '/' + clean_dashboard_name + '.json'
                print(f'DELETE {output_filename}')

def convert_dashboard(dashboard, dashboard_template):
    classic_metric_to_grail_metric_dict = get_classic_metric_to_grail_metric_dict()

    new_dashboard_json = copy.deepcopy(json.loads(dashboard_template))
    new_dashboard_tile_template = copy.deepcopy(new_dashboard_json.get('tiles').get('DATA_EXPLORER'))
    classic_dashboard_tiles = dashboard.get('tiles')
    new_dashboard_tiles = convert_dashboard_tiles(classic_dashboard_tiles, new_dashboard_tile_template)
    new_dashboard_json['tiles'] = new_dashboard_tiles

    new_dashboard_layout = configure_layout(len(new_dashboard_tiles))
    new_dashboard_json['layouts'] = new_dashboard_layout

    return new_dashboard_json


def convert_dashboard_tiles(classic_dashboard_tiles, new_dashboard_tile_template):
    new_dashboard_tiles = {}

    index = 0
    for classic_dashboard_tile in classic_dashboard_tiles:
        classic_dashboard_tile_type = classic_dashboard_tile.get('tileType')
        if classic_dashboard_tile_type != 'DATA_EXPLORER':
            # print(f'Unsupported Tile Type: {classic_dashboard_tile_type}')
            continue

        # TODO: Support these!
        if classic_dashboard_tile_type == 'MARKDOWN':
            continue
        if classic_dashboard_tile_type == 'HEADER':
            continue

        visualization = classic_dashboard_tile.get('visualConfig').get('type')
        if visualization == 'HEATMAP':
            # print(f'Unsupported Visualization: {visualization}')
            continue

        # print(f'Tile Type and Visualization: {classic_dashboard_tile_type} {visualization}')

        new_dashboard_tile = copy.deepcopy(new_dashboard_tile_template)
        new_dashboard_tile_string = json.dumps(new_dashboard_tile)
        classic_dashboard_tile_name = classic_dashboard_tile.get('name')
        classic_dashboard_queries = classic_dashboard_tile.get('queries')
        classic_dashboard_query = classic_dashboard_queries[0]
        # classic_dashboard_query_metric = classic_dashboard_query.get('metric')
        # classic_dashboard_query_aggregation = classic_dashboard_query.get('spaceAggregation')

        extracted_metric, extracted_aggregation, extracted_limit, extracted_sort_order = extract_query_parameters(classic_dashboard_query)

        # if not classic_dashboard_query_metric or not classic_dashboard_query_aggregation:
        #     classic_dashboard_query_metric = extract_metric_from_query_metric_selector(classic_dashboard_query)
        #     classic_dashboard_query_aggregation = extract_aggregation_from_query_metric_selector(classic_dashboard_query)
            
        grail_dashboard_metric_key = get_grail_metric_key(extracted_metric)
        new_dashboard_aggregation = convert_aggregation(extracted_aggregation)
        # if classic_dashboard_query_aggregation and classic_dashboard_query_aggregation != 'AVG' and classic_dashboard_query_aggregation != 'AUTO':
        #     print('DEBUG AGG:', classic_dashboard_tile_name, classic_dashboard_query_metric, classic_dashboard_query_aggregation, new_dashboard_aggregation)
        # if not classic_dashboard_query_aggregation:
        # print('DEBUG AGG:', classic_dashboard_tile_name, classic_dashboard_query_metric, classic_dashboard_query_aggregation, new_dashboard_aggregation)

        if grail_dashboard_metric_key == 'N/A':
            print(f'Skipping classic metric {extracted_metric} which is not supported in Grail')
            # print(f'{classic_dashboard_query_metric}')
            continue

        classic_dashboard_query_split_by = classic_dashboard_query.get('splitBy')
        if classic_dashboard_query_split_by:
            classic_dashboard_query_split_by = classic_dashboard_query_split_by[0]
        else:
            classic_dashboard_query_split_by = ''
        classic_dashboard_query_split_by = convert_dimension(classic_dashboard_query_split_by)
        new_dashboard_tile_string = new_dashboard_tile_string.replace('{{tile_name}}', classic_dashboard_tile_name)
        new_dashboard_tile_string = new_dashboard_tile_string.replace('{{metric_key}}', grail_dashboard_metric_key)
        new_dashboard_tile_string = new_dashboard_tile_string.replace('{{dimension_name}}', classic_dashboard_query_split_by)
        new_dashboard_tile_string = new_dashboard_tile_string.replace('{{aggregation_name}}', new_dashboard_aggregation)
        new_dashboard_function = get_aggregation_function(new_dashboard_aggregation)
        if not new_dashboard_function == 'INVALID':
            new_dashboard_tile_string = new_dashboard_tile_string.replace('{{function_name}}', new_dashboard_function)
            new_dashboard_tile_string = new_dashboard_tile_string.replace('{{sort_order}}', extracted_sort_order)
            new_dashboard_tile_string = new_dashboard_tile_string.replace('{{limit}}', str(extracted_limit))
            visualization = classic_dashboard_tile.get('visualConfig').get('type')
            if visualization:
                new_dashboard_tile_string = new_dashboard_tile_string.replace('{{visualization}}', convert_visualization(visualization))
            new_dashboard_tile_string = new_dashboard_tile_string.replace('{{field_name}}', grail_dashboard_metric_key.replace('dt.', ''))
            new_dashboard_tile_string = new_dashboard_tile_string.replace('{{metric_name}}', grail_dashboard_metric_key.replace('dt.', ''))
            # print(new_dashboard_tile_string)
            if not 'COMPLEX METRIC EXPRESSION' in new_dashboard_tile_string:
                new_dashboard_tile_string = new_dashboard_tile_string.replace('"Gives ', 'Gives ')
                new_dashboard_tile_string = new_dashboard_tile_string.replace('multi-session machines"', 'multi-session machines')
                new_dashboard_tile_string = new_dashboard_tile_string.replace('"4xx_error_sum"', '4xx_error_sum')
                new_dashboard_tile_string = new_dashboard_tile_string.replace('"5xx_error_sum"', '5xx_error_sum')
                # print(new_dashboard_tile_string)
                new_dashboard_tile = json.loads(new_dashboard_tile_string)
                new_dashboard_tiles[str(index)] = new_dashboard_tile
                # print('DEBUG FINAL:', classic_dashboard_tile_name, extracted_metric, extracted_aggregation, new_dashboard_aggregation, new_dashboard_function, extracted_limit, extracted_sort_order)
                index += 1

    return new_dashboard_tiles


def configure_layout(tile_count):
    layouts = {}

    index = 0

    x = 0
    y = 0
    w = 8
    h = 6

    while index < tile_count:
        key = str(index)
        layouts[key] = {"x": x, "y": y, "w": w, "h": h}
        y += h
        index += 1

    return layouts


def extract_query_parameters(classic_dashboard_query):
    extracted_metric = classic_dashboard_query.get('metric')
    extracted_aggregation = classic_dashboard_query.get('spaceAggregation')

    # extract parameters from the metric or metric selector as appropriate
    if extracted_metric and extracted_aggregation:
        extracted_limit = classic_dashboard_query.get('limit')
        if not extracted_limit:
            extracted_limit = 20
        extracted_sort_order = classic_dashboard_query.get('sortBy')
        if extracted_sort_order and extracted_sort_order == 'ASC':
            extracted_sort_order = 'asc'
        else:
            extracted_sort_order = 'desc'
    else:
        # print('Extracting metric from a metric selector...')
        classic_dashboard_query_metric_selector = classic_dashboard_query.get('metricSelector')
        classic_dashboard_query_metric_selector_split = classic_dashboard_query_metric_selector.split(':')
        # print('ms len:', len(classic_dashboard_query_metric_selector_split))
        # print('ms:', classic_dashboard_query_metric_selector_split)
        if len(classic_dashboard_query_metric_selector_split) >= 2:
            if classic_dashboard_query_metric_selector_split[0] == 'builtin':
                    # print('It is a builtin metric...')
                    extracted_metric = classic_dashboard_query_metric_selector_split[0] + ':' + classic_dashboard_query_metric_selector_split[1]
            else:
                extracted_metric = classic_dashboard_query_metric_selector_split[0]
        else:
            print(f'Metric selector must contain at least two strings after a split by ":".  Split: {classic_dashboard_query_metric_selector_split}')
            print(f'Metric selector: {classic_dashboard_query_metric_selector}')
            print(f'Metric selector split: {classic_dashboard_query_metric_selector_split}')
            exit(1)
        if len(classic_dashboard_query_metric_selector_split) >= 3:
            extracted_aggregation = classic_dashboard_query_metric_selector_split[3]
        else:
            extracted_aggregation = 'AUTO'
        if 'limit(' in classic_dashboard_query_metric_selector:
            extracted_limit = re.sub(r'.*limit\(', '', classic_dashboard_query_metric_selector)
            extracted_limit = re.sub(r'\).*', '', extracted_limit)
        else:
            extracted_limit = 20
        if 'sort(' in classic_dashboard_query_metric_selector:
            extracted_sort_order = re.sub(r'.*sort\(', '', classic_dashboard_query_metric_selector)
            extracted_sort_order = re.sub(r'\).*', '', extracted_sort_order)
            if 'ascending' in extracted_sort_order:
                extracted_sort_order = 'asc'
            else:
                extracted_sort_order = 'desc'
        else:
            extracted_sort_order = 'desc'

    if '(' in extracted_metric or ')' in extracted_metric:
        extracted_metric = f'COMPLEX METRIC EXPRESSION: {classic_dashboard_query_metric_selector}'

    return extracted_metric, extracted_aggregation, extracted_limit, extracted_sort_order


def convert_dimension(classic_dashboard_query_split_by):
    # return classic_dashboard_query_split_by.replace('dt.entity.host', 'host.name')
    # Do nothing for now, since the ID can be suppressed in the visualization while allowing intents based on ID
    return classic_dashboard_query_split_by


def convert_aggregation(classic_dashboard_query_aggregation):
    if not classic_dashboard_query_aggregation or classic_dashboard_query_aggregation == 'AUTO':
        return 'avg'
    else:
        return classic_dashboard_query_aggregation.lower()


def convert_visualization(classic_dashboard_visualization):
    if classic_dashboard_visualization == 'GRAPH_CHART':
        return 'lineChart'
    if classic_dashboard_visualization == 'TOP_LIST':
        return 'categoricalBarChart'
    if classic_dashboard_visualization == 'TABLE':
        return 'table'
    if classic_dashboard_visualization == 'SINGLE_VALUE':
        return 'singleValue'
    if classic_dashboard_visualization == 'PIE_CHART':
        return 'pieChart'
    if classic_dashboard_visualization == 'HONEYCOMB':
        return 'honeycomb'
    if classic_dashboard_visualization == 'STACKED_COLUMN':
        return 'barChart'

    # print(f'New Visualization: {classic_dashboard_visualization}')
    exit(1)


def get_aggregation_function(new_dashboard_aggregation):
    if new_dashboard_aggregation == 'count':
        return 'arraySize'

    if new_dashboard_aggregation in ['value', 'percentile_90']:
        return 'TODO'

    if new_dashboard_aggregation in ['avg', 'min', 'max', 'median', 'sum']:
        new_function = 'Array' + new_dashboard_aggregation.capitalize()
        return new_function

    # print(f'Invalid agg: {new_dashboard_aggregation}')
    # exit(1)

    return 'INVALID'


def get_dashboard_template():
    with open(DASHBOARD_TEMPLATE_FILE_NAME, 'r', encoding='utf-8') as f:
        dashboard_template = f.read()
        return dashboard_template


def get_grail_metric_key(classic_metric_key):
    global classic_metric_to_grail_metric_dict
    grail_metric_key = classic_metric_to_grail_metric_dict.get(classic_metric_key, 'N/A')
    if grail_metric_key == 'N/A':
        if classic_metric_key.startswith('builtin:tech'):
            if not classic_metric_key.startswith('builtin:tech.generic') and not classic_metric_key.startswith('builtin:tech.websphere'):

                # This affects too many non-extension process-level metrics, so assume few old extensions
                # and do it selectively if/when needed instead
                # grail_metric_key = classic_metric_key.replace('builtin:tech', 'legacy')

                grail_metric_key = 'N/A'
        else:
            if classic_metric_key.startswith('ext:'):
                grail_metric_key = convert_camel_to_snake(classic_metric_key.replace('ext:', ''))
            else:
                grail_metric_key = classic_metric_key

    print(classic_metric_key, grail_metric_key)

    return grail_metric_key


def get_classic_metric_to_grail_metric_dict():
    global classic_metric_to_grail_metric_dict
    classic_metric_to_grail_metric_dict = environment.get_configuration_object('classic_metric_to_grail_metric.yaml')
    return classic_metric_to_grail_metric_dict


def convert_camel_to_snake(key: str) -> str:
    """
    Convert CamelCase or camelCase string to snake_case.

    Examples:
        CamelCase -> camel_case
        camelCase -> camel_case
        getHTTPResponse -> get_http_response
    """
    if not key:
        return key

    # Handle standard camelCase / PascalCase transitions
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
    # Handle transitions like lower->upper or digit->upper
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)

    return s2.lower()


def main():
    convert_dashboards()


if __name__ == '__main__':
    main()
