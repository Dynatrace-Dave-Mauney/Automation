# Post all documents matching the file path pattern to the specified environment.

import codecs
import glob
import os

from Reuse import environment
from Reuse import new_platform_api


def run():
    """ Used when running directly from an IDE (or from a command line without using command line arguments) """

    # Post document(s) to the environment name, path, prefix and owner specified.
    # Wildcards like "?" to signify any single character or "*" to signify any number of characters may be used.
    # When wildcards are used, multiple documents may be referenced.
    # Example Paths:
    #  Single file reference:
    #   '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    #   '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000117.json'
    #  Multiple file reference (potentially, it depends on the content of the directory):
    #   'Sandbox/00000000-dddd-bbbb-aaaa-????????????.json' # Strict reference
    #   'Sandbox/*.json' # Lenient reference

    # post_dashboards('Personal', 'Dashboards/Assets/Key*.json')
    # post_launchpads('Personal', 'Launchpads/Downloads/Personal/Dave*.json')
    # post_notebooks('Personal', 'Notebooks/Assets/Best Practices.json')

    # post_dashboards(env, f'../$Private/Customers/$Current/Assets/NewPlatform/Dashboards/{env}/*.json')
    # post_dashboards(env, f'../$Private/$Output/Dashboards/ClassicConversion/*.json')
    # post_notebooks(env, f'../$Private/Customers/$Current/Assets/NewPlatform/Notebooks/{env}/*.json')

    # env='Sandbox'
    # env='PreProd'
    env='Prod'

    # Initial deployment
    # post_dashboards(env, f'Dashboards/Assets/Templates/*.json')
    # post_launchpads(env, 'Launchpads/Assets/*.json')

    # Add Management Zone Filtering
    post_dashboards(env, f'Dashboards/Assets/Entities by ManagementZone.json')
    post_dashboards(env, f'Dashboards/Assets/Key Metrics by ManagementZone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Hosts By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Hosts (Detailed) By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Java Memory By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Overview By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Services By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Service Errors By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Service HTTP Errors By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Web Servers By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Backend Overview By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Network (Host-Level Details) By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Network (Process-Level Details) By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Containers By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Go By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Node.js By Management Zone.json')
    post_dashboards(env, f'Dashboards/Assets/Templates/TEMPLATE Full Stack Overview By Management Zone.json')

def post_dashboards(env_name, path):
    post_documents(env_name, path, 'dashboard')


def post_launchpads(env_name, path):
    post_documents(env_name, path, 'launchpad')


def post_notebooks(env_name, path):
    post_documents(env_name, path, 'notebook')


def post_documents(env_name, path, document_type):
    friendly_function_name = 'Dynatrace Automation'
    _, env, client_id, client_secret = environment.get_client_environment_for_function(env_name, friendly_function_name)
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope='document:documents:write')
    for filename in glob.glob(path):
        if filename.endswith('.json') and not filename.endswith('metadata.json'):
            with codecs.open(filename, encoding='utf-8') as f:
                document = f.read()
                document_file_name = os.path.basename(filename)
                document_name = os.path.splitext(document_file_name)[0]
                formatted_document = document
                post_document(env_name, env, oauth_bearer_token, document_name, document_type, document_file_name, formatted_document)


def post_document(env_name, env, oauth_bearer_token, document_name, document_type, document_file_name, payload):
    if document_name.startswith('TEMPLATE'):
        document_name = document_name.replace('TEMPLATE', env_name.capitalize())
    print(f'Posting {document_type} "{document_name}" ({document_file_name}) to {env}')
    api_url = f'{env}/platform/document/v1/documents'
    headers = {'name': document_name, 'type': 'document', 'accept': 'application/json', 'Authorization': f'Bearer {str(oauth_bearer_token)}'}
    files = {'content': (document_file_name, payload, 'application/json')}
    params = {'name': document_name, 'type': document_type}
    new_platform_api.post_multipart_form_data(api_url, files=files, headers=headers, params=params)


if __name__ == '__main__':
    run()
