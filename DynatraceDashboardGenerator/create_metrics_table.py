"""
Load metrics file contents into SQLite3 database.

Command Line Notes:
C:\tools\sqlite3\sqlite3.exe c:\Dynatrace\Projects\Python\DynatraceDashboardGenerator\DynatraceDashboardGenerator.db
sqlite> select metric_id, json_extract(data, '$.displayName') from metrics where metric_id like '%generic.network%';
"""

import ast
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


def drop_metrics_table(conn):
    """
    Drop the metrics table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    try:
        cur.execute('DROP TABLE metrics')
    except Error as e:
        print(e)


def create_metrics_table(conn):
    """
    Create the metrics table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('CREATE TABLE metrics (metric_id varchar, data json)')


def load_metrics_table(conn):
    """
    Load the metrics table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    with open('metrics.json') as json_file:
        json_list = json.load(json_file)
        # print(type(json_list))
        # print(json_list)
        for json_dict in json_list:
            # print(type(json_dict))
            # print(json_dict)
            metric_id = json_dict.get('metricId')
            cur.execute('insert into metrics values (?, ?)',
                        [metric_id, json.dumps(json_dict)])
        conn.commit()


def select_all_metrics(conn):
    """
    Query all rows in the metrics table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT * FROM metrics')

    rows = cur.fetchall()

    for row in rows:
        print(row)


def select_metric_by_id(conn, metric_id):
    """
    Query metrics by metric_id
    :param conn: the Connection object
    :param metric_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT data FROM metrics WHERE metric_id = ?', (metric_id,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():
    database = r'DynatraceDashboardGenerator.db'

    # create a database connection
    conn = create_connection(database)
    with conn:
        print('1. Drop metrics table')
        drop_metrics_table(conn)

        print('2. Create metrics table')
        create_metrics_table(conn)

        print('3. Load metrics table')
        load_metrics_table(conn)

        print('4. Query metric by id:')
        select_metric_by_id(conn, 'builtin:host.cpu.usage')

        print('5. Query all metrics')
        select_all_metrics(conn)


if __name__ == '__main__':
    main()
