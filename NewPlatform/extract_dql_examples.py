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

    extract_dql_from_dashboards('Dashboards/Assets/*.json')

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




def extract_dql_from_dashboards(path):
    for filename in glob.glob(path):
        # print(filename)
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = f.read()
            dashboard_json = json.loads(dashboard)
            dashboard_file_name = os.path.basename(filename)
            dashboard_name = os.path.splitext(dashboard_file_name)[0]
            formatted_document = json.dumps(dashboard_json, indent=4, sort_keys=False)
            extract_dql_from_dashboard(dashboard_name, dashboard_file_name, formatted_document, dashboard_json)


def extract_dql_from_dashboard(dashboard_name, dashboard_file_name, formatted_document, dashboard_json):
    global fetch_bizevents
    global fetch_events
    global fetch_entity
    global fetch_logs
    global fetch_other
    print(f'Extracting from "{dashboard_name}" ({dashboard_file_name})')
    # print(f'{dashboard_json}')
    # print(f'{formatted_document}')
    # exit(1234)
    tiles = dashboard_json.get('tiles')
    keys = tiles.keys()
    for key in keys:
        query = tiles.get(key).get('query')
        if query:
            # print(f'{query}')
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
