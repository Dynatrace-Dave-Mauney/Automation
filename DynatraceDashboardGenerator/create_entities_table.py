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


def drop_entities_table(conn):
    """
    Drop the entities table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    try:
        cur.execute('DROP TABLE entities')
    except Error as e:
        print(e)


def create_entities_table(conn):
    """
    Create the entities table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('CREATE TABLE entities (entity_id varchar, data json)')


def load_entities_table(conn):
    """
    Load the entities table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    with open('entities.json') as json_file:
        json_list = json.load(json_file)
        # print(type(json_list))
        # print(json_list)
        for json_dict in json_list:
            # print(type(json_dict))
            # print(json_dict)
            entity_id = json_dict.get('entityId')
            cur.execute('insert into entities values (?, ?)',
                        [entity_id, json.dumps(json_dict)])
        conn.commit()

    conn.commit()


def select_all_entities(conn):
    """
    Query all rows in the entities table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT * FROM entities')

    rows = cur.fetchall()

    for row in rows:
        print(row)


def select_entity_by_id(conn, entity_id):
    """
    Query entities by entity_id
    :param conn: the Connection object
    :param entity_id:
    :return:
    """
    cur = conn.cursor()
    cur.execute('SELECT data FROM entities WHERE entity_id = ?', (entity_id,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():
    database = r'DynatraceDashboardGenerator.db'

    # create a database connection
    conn = create_connection(database)
    with conn:
        print('1. Drop entities table')
        drop_entities_table(conn)

        print('2. Create entities table')
        create_entities_table(conn)

        print('3. Load entities table')
        load_entities_table(conn)

        print('4. Query entity by id:')
        select_entity_by_id(conn, 'builtin:host.cpu.usage')

        print('5. Query all entities')
        select_all_entities(conn)


if __name__ == '__main__':
    main()