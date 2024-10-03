import glob
import json
import os
import codecs

fetch_bizevents = []
fetch_events = []
fetch_entity = []
fetch_logs = []
fetch_other = []


def run():
    global fetch_bizevents
    global fetch_events
    global fetch_entity
    global fetch_logs
    global fetch_other

    # extract_dql_from_documents('Dashboards/Assets/*.json')
    # extract_dql_from_documents('Notebooks/Assets/*.json')
    extract_dql_from_documents('customer_specific/*.json')

    print('')
    print('Bizevents:')
    for fetch_bizevent_query in fetch_bizevents:
        print(fetch_bizevent_query)

    print('')
    print('Events:')
    for fetch_events_query in fetch_events:
        print(fetch_events_query)

    print('')
    print('Entities:')
    for fetch_entity_query in fetch_entity:
        print(fetch_entity_query)

    print('')
    print('Logs:')
    for fetch_logs_query in fetch_logs:
        print(fetch_logs_query)

    print('')
    print('Other:')
    for fetch_other_query in fetch_other:
        print(fetch_other_query)


def extract_dql_from_documents(path):
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            document = f.read()
            document_json = json.loads(document)
            document_file_name = os.path.basename(filename)
            document_name = os.path.splitext(document_file_name)[0]
            # formatted_document = json.dumps(document_json, indent=4, sort_keys=False)
            extract_dql_from_document(document_name, document_file_name, document_json)


def extract_dql_from_document(document_name, document_file_name, document_json):
    global fetch_bizevents
    global fetch_events
    global fetch_entity
    global fetch_logs
    global fetch_other
    print(f'Extracting from "{document_name}" ({document_file_name})')

    sections = document_json.get('sections')

    if sections:
        for section in sections:
            document_type = section.get('type')
            if document_type == 'dql':
                query = section.get('state').get('input').get('value')
                if 'bizevents' in query:
                    fetch_bizevents.append(query)
                else:
                    if 'events' in query:
                        fetch_events.append(query)
                    else:
                        if 'entity' in query:
                            fetch_entity.append(query)
                        else:
                            if 'logs' in query:
                                fetch_logs.append(query)
                            else:
                                fetch_other.append(query)
    else:
        tiles = document_json.get('tiles')
        keys = tiles.keys()
        for key in keys:
            query = tiles.get(key).get('query')
            if query:
                if 'bizevents' in query:
                    fetch_bizevents.append(query)
                else:
                    if 'events' in query:
                        fetch_events.append(query)
                    else:
                        if 'entity' in query:
                            fetch_entity.append(query)
                        else:
                            if 'logs' in query:
                                fetch_logs.append(query)
                            else:
                                fetch_other.append(query)


if __name__ == '__main__':
    run()
