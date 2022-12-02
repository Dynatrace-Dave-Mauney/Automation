"""
Create a dashboard generator YAML file that drives which dashboards are generated and which tiles are included in
each dashboard.
"""

import copy
import json
import sqlite3
from sqlite3 import Error
import yaml


def get_dashboard_blueprint():
    with open('dashboard_blueprint.yaml', 'r') as file:
        document = file.read()
        return yaml.load(document, Loader=yaml.FullLoader)


def get_version():
    with open('version.json', 'r') as file:
        return json.load(file).get('version')


def convert_aggregation(aggregation_in):
    aggregation_out = aggregation_in.upper().replace('VALUE', 'NONE')
    return aggregation_out


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def generate_metrics_tiles(metrics, tiles_list):
    minimal_custom_charting_template = {'name': '', 'metric': '', 'aggregation': '', 'type': ''}

    conn = create_connection(r'DynatraceDashboardGenerator.db')
    with conn:
        cur = conn.cursor()
        # print(f'metrics pattern: {metrics[0]}')
        # Handle the metrics that require ranges
        if len(metrics) == 2:
            cur.execute('SELECT data FROM metrics WHERE metric_id BETWEEN "' +
                        metrics[0] + '" and "' + metrics[1] + '"')
        else:
            # Handle metrics that use typical "starts with" logic
            if len(metrics) == 1:
                cur.execute('SELECT data FROM metrics WHERE metric_id like "' + metrics[0] + '%"')
            else:
                print('Incorrect number of metrics in list...skipping...')

        rows = cur.fetchall()
        for row in rows:
            metric_dict = json.loads(row[0])
            tile_dict = minimal_custom_charting_template
            tile_dict['name'] = metric_dict['displayName']
            tile_dict['metric'] = metric_dict['metricId']
            tile_dict['type'] = 'LINE'
            tile_dict['aggregation'] = convert_aggregation(metric_dict['defaultAggregation']['type'])
            # print(tile_dict.get('metric'))
            tiles_list.append(copy.deepcopy(tile_dict))

    return tiles_list


def generate_entities_tiles(entities, service_type, tiles_list):
    minimal_entity_template = {'name': '', 'entity': ''}

    conn = create_connection(r'DynatraceDashboardGenerator.db')
    with conn:
        cur = conn.cursor()
        # Handle the entities that use typical "starts with" logic
        # Ranges are not (yet) supported
        if len(entities) == 1:
            cur.execute('SELECT data FROM entities WHERE entity_id like "' + entities[0] + '-%" order by entity_id')
        else:
            print('Incorrect number of entities in list...skipping...')

        rows = cur.fetchall()
        for row in rows:
            entity_dict = json.loads(row[0])
            print(entity_dict)
            # Skip rows where the "serviceType" is not a match for the "service_type" filter
            entity_service_type = entity_dict.get('properties').get('serviceType')
            if service_type:
                print(service_type + ' - ' + str(entity_service_type))
                if entity_service_type != service_type:
                    print('skipping')
                    continue
            tile_dict = minimal_entity_template
            tile_dict['name'] = entity_dict['displayName']
            tile_dict['entity'] = entity_dict['entityId']
            tiles_list.append(copy.deepcopy(tile_dict))

    return tiles_list


def main():
    dashboard_blueprint = get_dashboard_blueprint()
    minimal_dashboard_template = \
        {'name': '', 'id': '', 'owner': '', 'share': False, 'clusterVersion': '',
         'width': 1824, 'height': 5016, 'process': True}
    dashboard_blueprint_metadata = dashboard_blueprint.get('metadata')
    dashboard_template = minimal_dashboard_template
    dashboard_id_prefix = dashboard_blueprint_metadata['idPrefix']
    dashboard_template['owner'] = dashboard_blueprint_metadata['owner']
    dashboard_template['share'] = dashboard_blueprint_metadata['share']
    dashboard_template['clusterVersion'] = get_version()

    # Start a yaml list
    outfile = 'dashboard_controller.yaml'
    with open(outfile, 'w') as file:
        file.write('[\n')

    dashboard_counter = 0
    dashboards_count = len(dashboard_blueprint.get('dashboards'))

    for dashboard_dictionary in dashboard_blueprint.get('dashboards'):
        dashboard = dashboard_dictionary.get('dashboard')
        metrics = dashboard_dictionary.get('metrics', [])
        entities = dashboard_dictionary.get('entities', [])
        tiles = dashboard_dictionary.get('tiles', [])

        # For services, support splitting by service type
        service_type = None
        if entities and entities[0] == 'SERVICE':
            service_type = dashboard_dictionary.get('serviceType', None)

        dashboard_counter += 1
        dashboard_id = format(dashboard_counter, '012d')
        dashboard_template['id'] = dashboard_id_prefix + str(dashboard_id)
        dashboard_template['name'] = dashboard
        # print(dashboard + ':' + dashboard_template['id'])

        tiles_list = []

        if metrics:
            # print('generating metrics dashboards')
            generate_metrics_tiles(metrics, tiles_list)

        # TODO: Consider doing these later or separately.
        #       Just focus on metrics for now!
        # if entities:
        #    # print('generating entities dashboards')
        #    generate_entities_tiles(entities, service_type, tiles_list)

        # if tiles:
        #    # generic tiles can be passed "as is"
        #    tiles_list = tiles

        dashboard_template['tiles'] = tiles_list

        yaml.dumper.SafeDumper.ignore_aliases = lambda self, data: True
        yaml_string = yaml.dump(dashboard_template,
                                default_flow_style=True,
                                sort_keys=False,
                                Dumper=yaml.dumper.SafeDumper)

        # Remove extra spaces
        yaml_string = ' '.join(yaml_string.split())

        # Remove all newlines
        yaml_string = yaml_string.replace('\n', '')

        # Add newlines before each tile
        yaml_string = yaml_string.replace('[{name:', '[\n  {name:')
        yaml_string = yaml_string.replace(', {name:', ',\n  {name:')
        yaml_string = yaml_string.replace('[{tileType:', '[\n  {tileType:')
        yaml_string = yaml_string.replace(', {tileType:', ',\n  {tileType:')

        with open(outfile, 'a') as file:
            file.write(yaml_string)
            if dashboard_counter < dashboards_count:
                file.write(',')
            file.write('\n')

    with open(outfile, 'a') as file:
        file.write(']')


if __name__ == '__main__':
    main()
