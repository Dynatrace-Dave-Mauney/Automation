#
# TODO: Finish coding!
# Clone a document from one environment to another, changing environment-specific references
#

import codecs
import json
import glob
import os

from Reuse import environment
from Reuse import new_platform_api


document_type = 'launchpad'
always_use_alias = False

input_directory = '../$Private/Customers/$Current/Assets/NewPlatform/Launchpads/PreProd'
output_directory = '../$Private/Customers/$Current/Assets/NewPlatform/Launchpads/TEMP'


def run():
    clone_documents('PreProd', 'Sandbox', f'{input_directory}/*Launchpad.json')


def clone_documents(source_env_name, target_env_name, path):
    # print(f"clone_documents({env_name}, {path})")
    for filename in glob.glob(path):
        # Process document files (not document metadata files)
        if filename.endswith(".json") and not filename.endswith(".metadata.json"):
            with codecs.open(filename, encoding='utf-8') as f:
                document = f.read()
                document_file_name = os.path.basename(filename)
                document_name = os.path.splitext(document_file_name)[0]
                clone_document(source_env_name, target_env_name, document_name, document_file_name, document)


def clone_document(source_env_name, target_env_name, document_name, document_file_name, document):
    if document_type != 'launchpad':
        return

    print(f'Cloning {document_type} "{document_name}" ({document_file_name}) from {source_env_name} to {target_env_name}')

    document = replace_tenant_specific_strings(source_env_name, target_env_name, document)

    with open(f'{output_directory}/{document_file_name}', 'bw') as file:
        file.write(bytes(document, encoding="utf-8"))


    # document_json = json.loads(document)
    #
    # # dashboard_links = document_json['containerList']['containers']['blocks']
    # document_containers = document_json['containerList']['containers']
    #
    # new_document_blocks = []
    # for document_container in document_containers:
    #     document_blocks = document_container['blocks']
    #     for document_block in document_blocks:
    #         document_block_type = document_block['type']
    #         document_block_content = document_block['content']
    #         if document_block_type and document_block_content:
    #             if document_block_type == 'markdown' and source_env_name.lower() in document_block_content.lower():
    #                 document_block_content = replace_tenant_specific_strings(source_env_name, target_env_name, document_block_content)
    #                 new_document_block_content = document_block_content
    #                 new_document_blocks.append(new_document_block_content)
    #
    # document_json['containerList']['containers']['blocks'] = new_document_blocks
    # print(document_json)

def replace_tenant_specific_strings(source_env_name, target_env_name, document):
    source_prefix = get_prefix(source_env_name)
    target_prefix = get_prefix(target_env_name)
    source_tenant = get_tenant(source_env_name)
    target_tenant = get_tenant(target_env_name)
    source_tenant_alias = get_tenant_alias(source_env_name)
    target_tenant_alias = get_tenant_alias(target_env_name)
    document = document.replace(source_prefix, target_prefix)
    document = document.replace(source_tenant, target_tenant)
    document = document.replace(source_tenant_alias, target_tenant_alias)
    return document


def get_prefix(env_name):
    if env_name.lower() == 'sandbox':
        return "Sandbox"
    else:
        if env_name.lower() == 'preprod':
            return "Preprod"
        else:
            if env_name.lower() == 'prod':
                return "Prod"
            else:
                print(f'Unsupported environment name: {env_name}')
                exit(1)


def get_tenant(env_name):
    sandbox = "kqt47535"
    preprod = "agn93468"
    prod = "hgj78449"

    if always_use_alias:
        sandbox = "kroger-sandbox"
        preprod = "kroger-nonprod"
        prod = "kroger-prod"

    if env_name.lower() == 'sandbox':
        return "kqt47535"
    else:
        if env_name.lower() == 'preprod':
            return "agn93468"
        else:
            if env_name.lower() == 'prod':
                return "hgj78449"
            else:
                print(f'Unsupported environment name: {env_name}')
                exit(1)


def get_tenant_alias(env_name):
    if env_name.lower() == 'sandbox':
        return "kroger-sandbox"
    else:
        if env_name.lower() == 'preprod':
            return "kroger-nonprod"
        else:
            if env_name.lower() == 'prod':
                return "kroger-prod"
            else:
                print(f'Unsupported environment name: {env_name}')
                exit(1)


if __name__ == '__main__':
    run()
