import glob
import json
import os
import codecs

code_list = []


def run():
    global code_list

    # extract_dql_from_documents('Dashboards/Assets/*.json')
    # extract_dql_from_documents('Notebooks/Assets/*.json')
    extract_dql_from_documents('customer_specific/CONV*.json')

    print('')
    print('Code:')
    for code in code_list:
        print(code)


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
    global code_list
    print(f'Extracting from "{document_name}" ({document_file_name})')

    sections = document_json.get('sections')

    # Process Notebook
    if sections:
        for section in sections:
            document_type = section.get('type')
            if document_type == 'function':
                query = section.get('state').get('input').get('value')
                code_list.append(query)
    else:
        # Process Dashboard
        tiles = document_json.get('tiles')
        keys = tiles.keys()
        for key in keys:
            tile = tiles.get(key)
            tile_type = tile.get('type')
            query = tiles.get(key).get('input')
            if query:
                code_list.append(query)


if __name__ == '__main__':
    run()
