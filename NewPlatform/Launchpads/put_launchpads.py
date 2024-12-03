# Put all dashboards matching the file path pattern to the specified environment.

# import json
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

    put_dashboards('Personal', "Downloads/Personal/Dave's Launchpad.json")


def put_dashboards(env_name, path):
    # print(f"put_dashboards({env_name}, {path})")
    friendly_function_name = 'Dynatrace Automation'
    _, env, client_id, client_secret = environment.get_client_environment_for_function(env_name, friendly_function_name)
    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope='document:documents:read document:documents:write')
    for filename in glob.glob(path):
        # Process dashboard files (not dashboard metadata files)
        if filename.endswith(".json") and not filename.endswith(".metadata.json"):
            with codecs.open(filename, encoding='utf-8') as f:
                dashboard = f.read()
                # Python JSON parser cannot handle at least one TechShady dashboard, so skip parsing
                # dashboard_json = json.loads(dashboard)
                dashboard_file_name = os.path.basename(filename)
                dashboard_name = os.path.splitext(dashboard_file_name)[0]
                # formatted_document = json.dumps(dashboard_json, indent=4, sort_keys=False)
                formatted_document = dashboard
                dashboard_id = get_dashboard_metadata(filename)
                # print("Dashboard ID:", dashboard_id, json.loads(dashboard))
                put_dashboard(env, oauth_bearer_token, dashboard_name, dashboard_id, dashboard_file_name, formatted_document)


def get_dashboard_metadata(filename):
    dashboard_metadata_filename = filename.replace(".json", ".metadata.json")
    with codecs.open(dashboard_metadata_filename, encoding='utf-8') as f:
        dashboard_metadata = json.loads(f.read())
        return dashboard_metadata.get("id")


def put_dashboard(env, oauth_bearer_token, dashboard_name, dashboard_id, dashboard_file_name, payload):
    print(f'Putting "{dashboard_name}" ({dashboard_file_name}) to {env}')
    api_url = f'{env}/platform/document/v1/documents'
    headers = {'accept': 'application/json', 'Authorization': f'Bearer {str(oauth_bearer_token)}'}
    files = {'content': (dashboard_file_name, payload, 'application/json')}
    optimistic_locking_version = get_optimistic_locking_version(env, oauth_bearer_token, dashboard_id)
    params = f'optimistic-locking-version={optimistic_locking_version}'
    new_platform_api.put_multipart_form_data(f"{api_url}/{dashboard_id}/content", files=files, headers=headers, params=params)


def get_optimistic_locking_version(env, oauth_bearer_token, dashboard_id):
    dashboard_results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents/{dashboard_id}/metadata', None)
    dashboard_json = json.loads(dashboard_results.text)
    document_version = dashboard_json.get("version")
    payload_dict = {"documentVersion": document_version, "lockDurationInSeconds": 10}
    payload = json.dumps(payload_dict)
    dashboard_lock_results = new_platform_api.post(oauth_bearer_token, f'{env}/platform/document/v1/documents/{dashboard_id}:acquire-lock', payload)
    optimistic_locking_version = json.loads(dashboard_lock_results.text).get("documentVersion")
    return optimistic_locking_version


if __name__ == '__main__':
    run()
