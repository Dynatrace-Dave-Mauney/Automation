"""
Load dashboard and tile templates from dashboard template JSON file into SQLite3 database.

Command Line Notes:
C:\tools\sqlite3\sqlite3.exe c:\Dynatrace\Projects\Python\DynatraceDashboardGenerator\DynatraceDashboardGenerator.db
sqlite> select template_id from templates where template_id <> 'dashboard';
"""

import json
import sqlite3
from sqlite3 import Error


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


def drop_templates_table(conn):
    """
    Drop the templates table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    try:
        cur.execute('DROP TABLE templates')
    except Error as e:
        print(e)


def create_templates_table(conn):
    """
    Create the templates table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('CREATE TABLE templates (template_id varchar, data json)')


def load_templates_table(conn):
    """
    Load the templates table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    with open('dashboard_template.json', 'r') as file:
        dashboard_template_json = file.read()

    dashboard = json.loads(dashboard_template_json)

    # Set some default values that will always be replace for the dashboard
    dashboard['dashboardMetadata']['name'] = 'TEMPLATE'
    dashboard['id'] = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    dashboard['dashboardMetadata']['owner'] = 'nobody@example.com'
    dashboard['metadata']['clusterVersion'] = ''
    dashboard['metadata']['configurationVersions'] = [0]
    dashboard['dashboardMetadata']['shared'] = False
    dashboard['dashboardMetadata']['sharingDetails']['linkShared'] = False
    dashboard['dashboardMetadata']['sharingDetails']['published'] = False
    dashboard['dashboardMetadata']['dashboardFilter']['timeframe'] = ''
    # None in Python gets converted to null in JSON
    dashboard['dashboardMetadata']['dashboardFilter']['managementZone'] = None

    tiles = dashboard.get('tiles')
    for tile in tiles:
        tile_type = tile.get('tileType')
        tile_width = tile.get('bounds').get('width')
        tile_height = tile.get('bounds').get('height')
        tile_chart_visible = tile.get('chartVisible')

        if tile_type != 'DATA_EXPLORER' and tile_type != 'DATA_EXPLORER_CODE':
            # For simplicity, empty the tiles of all meaningful data generically and then set some fields back to their original values
            tile = reset_dictionary(tile)
            tile['tileType'] = tile_type
            tile['configured'] = True
            tile['bounds']['width'] = tile_width
            tile['bounds']['height'] = tile_height
            if tile_chart_visible:
                tile['chartVisible'] = tile_chart_visible

        template_id = tile_type
        cur.execute('insert into templates values (?, ?)',
                    [template_id, json.dumps(tile)])

    dashboard['tiles'] = []
    template_id = 'dashboard'
    cur.execute('insert into templates values (?, ?)',
                [template_id, json.dumps(dashboard)])


def select_all_templates(conn):
    """
    Query all rows in the templates table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT * FROM templates order by template_id')

    rows = cur.fetchall()

    for row in rows:
        print(row)


def select_template_by_id(conn, template_id):
    """
    Query templates by template_id
    :param conn: the Connection object
    :param template_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT data FROM templates WHERE template_id = ?', (template_id,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


def reset_dictionary(any_dict):
    for key in any_dict.keys():
        value = any_dict[key]
        if type(value) == bool:
            any_dict[key] = False
        if type(value) == int:
            any_dict[key] = 0
        if type(value) == str:
            any_dict[key] = ''
        if type(value) == dict:
            any_dict[key] = reset_dictionary(value)
        if type(value) == list:
            any_dict[key] = reset_list(value)
    return any_dict

def reset_list(any_list):
    # The only known cases are string and dictionary.
    # For string, it needs to just be emptied.
    # For dictionary, it needs to be reset.
    for (i, value) in enumerate(any_list):
        if type(value) == str:
            any_list = []
        if type(value) == dict:
            any_list[i] = reset_dictionary(value)
    return any_list


def main():
    database = r'DynatraceDashboardGenerator.db'

    # create a database connection
    conn = create_connection(database)
    with conn:
        # print('1. Drop templates table')
        # drop_templates_table(conn)
        #
        # print('2. Create templates table')
        # create_templates_table(conn)
        #
        # print('3. Load templates table')
        # load_templates_table(conn)
        #
        # print('4. Query template by id:')
        # select_template_by_id(conn, 'dashboard')
        # select_template_by_id(conn, 'CUSTOM_CHARTING')

        print('5. Query all templates')
        select_all_templates(conn)


if __name__ == '__main__':
    main()
