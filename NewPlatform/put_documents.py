# Put all documents matching the file path pattern to the specified environment.

# The content must be in a file named like "docname.json" and a corresponding metadata
# file ending with ".metadata.json" instead of ".json", like "docname.metadata.json"

# You can create these files by running the "download" python module for the
# desired document type (Dashboards/download_dashboards.py, for example).

import codecs
import json
import glob
import os

from Reuse import environment
from Reuse import new_platform_api


def run():
    """ Used when running directly from an IDE (or from a command line without using command line arguments) """

    # Put document(s) to the environment name, path, prefix and owner specified.
    # Wildcards like "?" to signify any single character or "*" to signify any number of characters may be used.
    # When wildcards are used, multiple documents may be referenced.
    # Example Paths:
    #  Single file reference:
    #   '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    #   '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000117.json'
    #  Multiple file reference (potentially, it depends on the content of the directory):
    #   'Sandbox/00000000-dddd-bbbb-aaaa-????????????.json' # Strict reference
    #   'Sandbox/*.json' # Lenient reference

    # put_documents('tenant1', '../$Private/Customers/$Current/Assets/NewPlatform/Launchpads/tenant1/Dynatrace Architecture Launchpad.json')
    # put_documents('tenant1', '../$Private/Customers/$Current/Assets/NewPlatform/Launchpads/tenant1/Dynatrace User Launchpad.json')
    # put_documents('tenant1', '../$Private/Customers/$Current/Assets/NewPlatform/Notebooks/tenant1/*.json')
    # put_documents('tenant1', '../$Private/Customers/$Current/Assets/NewPlatform/Dashboards/tenant1/*.json')

    put_documents('Prod', '../$Private/Customers/$Current/Assets/NewPlatform/Launchpads/Prod/Dynatrace Architecture Launchpad.json')
    put_documents('Prod', '../$Private/Customers/$Current/Assets/NewPlatform/Launchpads/Prod/Dynatrace User Launchpad.json')


def put_documents(env_name, path):
    # print(f"put_documents({env_name}, {path})")
    friendly_function_name = 'Dynatrace Automation'
    _, env, client_id, client_secret = environment.get_client_environment_for_function(env_name, friendly_function_name)
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope='document:documents:read document:documents:write')
    for filename in glob.glob(path):
        # Process document files (not document metadata files)
        if filename.endswith(".json") and not filename.endswith(".metadata.json"):
            with codecs.open(filename, encoding='utf-8') as f:
                document = f.read()
                document_file_name = os.path.basename(filename)
                document_name = os.path.splitext(document_file_name)[0]
                formatted_document = document
                document_metadata = get_document_metadata(filename)
                document_id = document_metadata.get('id')
                document_type = document_metadata.get('type')
                put_document(env, oauth_bearer_token, document_name, document_id, document_type, document_file_name, formatted_document)


def get_document_metadata(filename):
    document_metadata_filename = filename.replace(".json", ".metadata.json")
    with codecs.open(document_metadata_filename, encoding='utf-8') as f:
        document_metadata = json.loads(f.read())
        return document_metadata


def put_document(env, oauth_bearer_token, document_name, document_id, document_type, document_file_name, payload):
    print(f'Putting {document_type} "{document_name}" ({document_file_name}) to {env}')
    api_url = f'{env}/platform/document/v1/documents'
    headers = {'accept': 'application/json', 'Authorization': f'Bearer {str(oauth_bearer_token)}'}
    files = {'content': (document_file_name, payload, 'application/json')}
    optimistic_locking_version = get_optimistic_locking_version(env, oauth_bearer_token, document_id)
    params = f'optimistic-locking-version={optimistic_locking_version}'
    new_platform_api.put_multipart_form_data(f"{api_url}/{document_id}/content", files=files, headers=headers, params=params)

    # print(payload)

def get_optimistic_locking_version(env, oauth_bearer_token, document_id):
    document_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}/metadata', None)
    document_json = json.loads(document_results.text)
    document_version = document_json.get("version")
    payload_dict = {"documentVersion": document_version, "lockDurationInSeconds": 10}
    payload = json.dumps(payload_dict)
    document_lock_results = new_platform_api.post(oauth_bearer_token, f'{env}/platform/document/v1/documents/{document_id}:acquire-lock', payload)
    optimistic_locking_version = json.loads(document_lock_results.text).get("documentVersion")
    return optimistic_locking_version


if __name__ == '__main__':
    run()
