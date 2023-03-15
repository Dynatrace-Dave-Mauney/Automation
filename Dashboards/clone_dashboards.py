"""

For safety, a clone will only be done for a specific dashboard.

Remove the if statement to clone all dashboards.

"""

import json
import os
import ssl
import requests
from inspect import currentframe
from requests import Response

from Reuse import dynatrace_api
from Reuse import environment


def get_by_object_id(env, token, endpoint, object_id):
    url = env + endpoint + '/' + object_id
    try:
        r = requests.get(url, params='', headers={'Authorization': 'Api-Token ' + token})
        if r.status_code not in [200]:
            print('Error in "get_by_object_id(endpoint, object_id)" method')
            print('Endpoint: ' + endpoint)
            print('Object ID: ' + object_id)
            print('Exit code shown below is the source code line number of the exit statement invoked')
            exit(get_line_number())
        return json.loads(r.text)
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def post(env, token, endpoint: str, payload: str) -> Response:
    # In general, avoid post in favor of put so "fixed ids" can be used
    json_data = json.loads(payload)
    # Remove id if present
    # print(f'Popped: {json_data.pop("id")}')
    json_data.pop("id")
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r: Response = requests.post(url, formatted_payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        # print('Status Code: %d' % r.status_code)
        # print('Reason: %s' % r.reason)
        # if len(r.text) > 0:
        #     print(r.text)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                name = json_data.get('name')
                if name:
                    print('Name: ' + name)
                print('Error in "post(endpoint, payload)" method')
                print('Exit code shown below is the source code line number of the exit statement invoked')
                print('See ' + error_filename + ' for more details')
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def put(env, token, endpoint, object_id, payload):
    # In general, favor put over post so "fixed ids" can be used
    # print(endpoint, object_id, payload)
    name = json.loads(payload).get('dashboardMetadata').get('name')

    json_data = json.dumps(json.loads(payload), indent=4, sort_keys=False)
    url = env + endpoint + '/' + object_id
    try:
        r: Response = requests.put(url, json_data.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code == 201:
            print('Added ' + name + ': ' + object_id + ' (' + endpoint + ')')
        else:
            if r.status_code == 204:
                print('Updated ' + name + ': ' + object_id + ' (' + endpoint + ')')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
        if r.status_code not in [200, 201, 204]:
            error_filename = '$put_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(json_data)
                print('Error in "put(endpoint, object_id, payload)" method')
                print('Exit code shown below is the source code line number of the exit statement invoked')
                print('See ' + error_filename + ' for more details')
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def process(source_env, source_token, target_env, target_token):
    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboard_json_list = dynatrace_api.get(source_env, source_token, endpoint, params)
    for dashboard_json in dashboard_json_list:
        inner_dashboard_json_list = dashboard_json.get('dashboards')
        for inner_dashboard_json in inner_dashboard_json_list:
            dashboard_id = inner_dashboard_json.get('id')
            dashboard_name = inner_dashboard_json.get('name')
            if dashboard_id == 'de71298c-84a2-4ee9-bfd1-b4bd7b5ed4ef':
                dashboard = get_by_object_id(source_env, source_token, endpoint, dashboard_id)
                # To change the owner
                # owner = dashboard.get('dashboardMetadata').get('owner')
                # dashboard['dashboardMetadata']['owner'] = 'nobody@example.com'
                # You may want to use POST if cloning in the same tenant.
                # But generally, PUT is preferred, when "fixed ids' are used.
                # response = post(target_env, target_token, endpoint, json.dumps(dashboard, indent=4, sort_keys=False))
                response = put(target_env, target_token, endpoint, dashboard_id, json.dumps(dashboard, indent=4, sort_keys=False))
                if response.status_code == 204:
                    print(f'Cloned {dashboard_name} ({dashboard_id}) from {source_env} to {target_env} with same name and id as an UPDATE')
                else:
                    new_dashboard_id = json.loads(response.text).get('id')
                    print(f'Cloned {dashboard_name} ({dashboard_id}) from {source_env} to {target_env} with same name and id of {new_dashboard_id}')


def main():
    source_env_name = 'Personal'
    target_env_name = 'FreeTrial1'
    env_name, source_env, source_token = environment.get_environment(source_env_name)
    env_name, target_env, target_token = environment.get_environment(target_env_name)
    process(source_env, source_token, target_env, target_token)


if __name__ == '__main__':
    main()
