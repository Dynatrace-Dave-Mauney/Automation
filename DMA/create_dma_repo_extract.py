import glob
import json
import os
import re

from json import JSONDecodeError
from pathlib import Path

# DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards'
# NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks'

DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards-Testing'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks-Testing'

# OUTPUT_FILE_NAME = '$DMA_Repo_Extract.json'
OUTPUT_FILE_NAME = '$DMA_Repo_Extract-Testing.json'

include_dashboards = True
include_notebooks = True


def process():
    documents = []

    if include_dashboards:
        dashboard_extract = create_dashboard_extract()
        documents.extend(dashboard_extract)
        # print(dashboard_extract)
        # formatted_json = json.dumps(dashboard_extract, indent=4, sort_keys=False)
        # print(formatted_json)

    if include_notebooks:
        notebook_extract = create_notebook_extract()
        documents.extend(notebook_extract)
        # print(notebook_extract)
        # formatted_json = json.dumps(notebook_extract, indent=4, sort_keys=False)
        # print(formatted_json)

    dma_extract = {
        'name': 'DMA Repo Extract',
        'description': 'DMA Repo Documents extract of DQL/SPL and buckets for easier analysis and processing.',
        'documents': documents
    }

    output_json = json.dumps(dma_extract, indent=4, sort_keys=False)
    print(output_json)

    output_filename = OUTPUT_FILE_NAME
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(output_json)


def create_dashboard_extract():
    document_metadata_by_file_stem = {}
    results = []

    for filename in glob.glob(DASHBOARD_REPO_PATH + '/*'):
        if os.path.isfile(filename):
            if filename.endswith('.metadata.json'):
                file_stem = Path(filename).stem
                file_stem = Path(file_stem).stem
                document_metadata = get_document_metadata(filename)
                document_metadata_by_file_stem[file_stem] = document_metadata

    for filename in glob.glob(DASHBOARD_REPO_PATH + '/*'):
        if os.path.isfile(filename):
            if 'metadata' not in filename and filename.endswith('.json'):
                file_stem = Path(filename).stem
                normalized_file_stem = file_stem.replace('[Splunk] ', '')

                document_metadata = document_metadata_by_file_stem.get(file_stem)
                document_dict = {
                    'document_id': document_metadata.get('id'),
                    'document_name': document_metadata.get('name'),
                    'document_type': document_metadata.get('type'),
                    'document_items': [],
                }

                with open(filename, 'r', encoding='utf-8') as f:
                    infile_content = f.read()
                try:
                    infile_content_json = json.loads(infile_content)
                    dashboard_tiles = infile_content_json.get('tiles')
                    dashboard_tile_keys = dashboard_tiles.keys()
                    for dashboard_tile_key in dashboard_tile_keys:
                        dashboard_tile_dict = dashboard_tiles[dashboard_tile_key]
                        dashboard_tile_query = dashboard_tile_dict.get('query')
                        if dashboard_tile_query:
                            bucket_match = re.search(r'bucket:\s*\{"([^"]+)"\}', dashboard_tile_query)
                            bucket_name = bucket_match.group(1) if bucket_match else None
                            index_name = extract_index(dashboard_tile_query)
                            document_dict['document_items'].append({
                                'id': dashboard_tile_key,
                                'dql': dashboard_tile_dict.get('query'),
                                'bucket': bucket_name,
                                'index': index_name,
                            })

                except JSONDecodeError:
                    print(f'Skipping due to non-JSON file content: {filename}')

                results.append(document_dict)

    return results


def extract_index(text):
    # print('text:', text)

    spl_match = re.search(r'======= ORIGINAL SPL =======(.*?)======= END ORIGINAL SPL =======', text, re.DOTALL)

    print('spl_match:', spl_match)
    if not spl_match:
        return None

    spl_text = spl_match.group(1)
    # print('spl_text:', spl_text)

    # Extract index value with or without quotes/escaped quotes
    index_match = re.search(
        r'index=(?:\\?"?)?([A-Za-z0-9_-]+)(?:\\?"?)?',
        spl_text
    )

    # print(index_match)
    # if index_match:
    #     print('index:', index_match.group(1))

    return index_match.group(1) if index_match else None


def create_notebook_extract():
    document_metadata_by_file_stem = {}
    results = []

    for filename in glob.glob(NOTEBOOK_REPO_PATH + '/*'):
        if os.path.isfile(filename):
            if filename.endswith('.metadata.json'):
                file_stem = Path(filename).stem
                file_stem = Path(file_stem).stem
                document_metadata = get_document_metadata(filename)
                document_metadata_by_file_stem[file_stem] = document_metadata

    for filename in glob.glob(NOTEBOOK_REPO_PATH + '/*'):
        if os.path.isfile(filename):
            if 'metadata' not in filename and filename.endswith('.json'):
                file_stem = Path(filename).stem
                normalized_file_stem = file_stem.replace('[ALERT] - ', '')
                normalized_file_stem = normalized_file_stem.replace('[REPORT] - ', '')
                normalized_file_stem = normalized_file_stem.replace('[SEARCH] - ', '')

                document_metadata = document_metadata_by_file_stem.get(file_stem)
                document_dict = {
                    'document_id': document_metadata.get('id'),
                    'document_name': document_metadata.get('name'),
                    'document_type': document_metadata.get('type'),
                    'document_items': [],
                }

                with open(filename, 'r', encoding='utf-8') as f:
                    infile_content = f.read()
                try:
                    infile_content_json = json.loads(infile_content)
                    notebook_sections = infile_content_json.get('sections')
                    for notebook_section_value in notebook_sections:
                        notebook_section_value_type = notebook_section_value.get('type')
                        if notebook_section_value_type == 'dql':
                            notebook_section_value_state = notebook_section_value.get('state')
                            notebook_section_value_state_input_value = notebook_section_value_state.get('input', {}).get('value')

                            bucket_match = re.search(r'bucket:\s*\{"([^"]+)"\}', notebook_section_value_state_input_value)
                            bucket_name = bucket_match.group(1) if bucket_match else None
                            index_name = extract_index(notebook_section_value_state_input_value)
                            document_dict['document_items'].append({
                                'id': notebook_section_value.get('id'),
                                'dql': notebook_section_value_state_input_value,
                                'bucket': bucket_name,
                                'index': index_name,
                            })

                            # OBSOLETE
                            # match = re.search(r'bucket:\s*\{"([^"]+)"\}', notebook_section_value_state_input_value)
                            # if match:
                            #     bucket_name = match.group(1)
                            #     document_dict['document_items'].append({
                            #         'id': notebook_section_value.get('id'),
                            #         'dql': notebook_section_value_state_input_value,
                            #         'bucket': bucket_name,
                            #     })
                            #
                            # results.append(document_dict)

                except JSONDecodeError:
                    print(f'Skipping due to non-JSON file content: {filename}')

                results.append(document_dict)

    return results


def get_document_metadata(filename):
    selected_keys = ["id", "name", "type"]
    with open(filename, 'r', encoding='utf-8') as f:
        infile_content = f.read()
        data = json.loads(infile_content)
        filtered_json = {key: data[key] for key in selected_keys if key in data}
        return filtered_json


if __name__ == '__main__':
    process()
