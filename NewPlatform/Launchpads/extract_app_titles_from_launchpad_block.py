import glob
import json
import os
import codecs


def process():
    extract_dictionary_from_launchpad_blocks('Assets/QuickApplicationLinks.json')


def extract_dictionary_from_launchpad_blocks(path):
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            document = f.read()
            document_json = json.loads(document)
            document_file_name = os.path.basename(filename)
            document_name = os.path.splitext(document_file_name)[0]
            # formatted_document = json.dumps(document_json, indent=4, sort_keys=False)
            extract_dictionary_from_launchpad_block(document_name, document_file_name, document_json)


def extract_dictionary_from_launchpad_block(document_name, document_file_name, document_json):
    print(f'Extracting from "{document_name}" ({document_file_name})')

    block_content_list = document_json.get('containerList').get('containers')[0].get('blocks')[0].get('content')

    # Process Application Links Block
    if block_content_list:
        for link in block_content_list:
            link_title = link.get('title')
            # link_id = link.get('id')
            # link_action_app_id = link.get('appId')
            # link_icon = link.get('icon')
            # print(link_title, link_id, link_action_app_id, link_icon)
            print(f"\t'{link_title}',")


if __name__ == '__main__':
    process()
