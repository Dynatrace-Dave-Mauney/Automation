# Put all dashboards matching the file path pattern to the specified environment.

import json
import glob
import os
import codecs

from Reuse import new_platform_api
from Reuse import environment


def run():
    """ Used when running directly from an IDE (or from a command line without using command line arguments) """

    # Put dashboard(s) to the environment name, path, prefix and owner specified.
    # Wildcards like "?" to signify any single character or "*" to signify any number of characters may be used.
    # When wildcards are used, multiple dashboards may be referenced.
    # Example Paths:
    #  Single file reference:
    #   '../$Input/Dashboards/Examples/00000000-0000-0000-0000-000000000000.json'
    #   '../DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-dddd-000000000117.json'
    #  Multiple file reference (potentially, it depends on the content of the directory):
    #   'Sandbox/00000000-dddd-bbbb-aaaa-????????????.json' # Strict reference
    #   'Sandbox/*.json' # Lenient reference

    post_dashboards('Personal', 'Assets/*.json')
    post_dashboards('Personal', 'Assets/External/CustomerSuccess/*.json')
    post_dashboards('Personal', 'Assets/External/TechShady/*.json')


def post_dashboards(env_name, path):
    friendly_function_name = 'Dynatrace Platform Document'
    _, env, client_id, client_secret = environment.get_client_environment_for_function(env_name, friendly_function_name)
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope='document:documents:write')
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = f.read()
            # Python JSON parser cannot handle at least one TechShady dashboard, so skip parsing
            # dashboard_json = json.loads(dashboard)
            dashboard_file_name = os.path.basename(filename)
            dashboard_name = os.path.splitext(dashboard_file_name)[0]
            # formatted_document = json.dumps(dashboard_json, indent=4, sort_keys=False)
            formatted_document = dashboard
            post_dashboard(env, oauth_bearer_token, dashboard_name, dashboard_file_name, formatted_document)


def post_dashboard(env, oauth_bearer_token, dashboard_name, dashboard_file_name, payload):
    print(f'Posting "{dashboard_name}" ({dashboard_file_name}) to {env}')
    api_url = f'{env}/platform/document/v1/documents'
    headers = {'name': dashboard_name, 'type': 'dashboard', 'accept': 'application/json', 'Authorization': f'Bearer {str(oauth_bearer_token)}'}
    files = {'content': (dashboard_file_name, payload, 'application/json')}
    params = {'name': dashboard_name, 'type': 'dashboard'}
    new_platform_api.post_multipart_form_data(api_url, files=files, headers=headers, params=params)


if __name__ == '__main__':
    run()
