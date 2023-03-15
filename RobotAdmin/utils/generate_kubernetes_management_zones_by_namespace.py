import copy
import json
import requests
import ssl
import urllib.parse
from inspect import currentframe
from requests import Response

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    # Get all namespaces
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=1000&entitySelector=type(CLOUD_APPLICATION_NAMESPACE)'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    kubernetes_namespaces_json_list = dynatrace_api.get(env, token, endpoint, params)

    # Get all hosts with "Kubernetes Namespace" tag(s)
    endpoint = '/api/v2/entities'
    raw_params = 'entitySelector=type(HOST),tag("Kubernetes Namespace")&fields=+tags'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts_json_list = dynatrace_api.get(env, token, endpoint, params)

    namespaces = []
    for kubernetes_namespaces_json in kubernetes_namespaces_json_list:
        inner_kubernetes_namespaces_json_list = kubernetes_namespaces_json.get('entities')
        for inner_kubernetes_namespaces_json in inner_kubernetes_namespaces_json_list:
            display_name = inner_kubernetes_namespaces_json.get('displayName')
            # Only generate management zones for namespaces tagging one or more hosts
            search_namespace = "'Kubernetes Namespace', 'value': '" + display_name + "'"
            if search_namespace in str(hosts_json_list):
                if display_name not in namespaces:
                    namespaces.append(display_name)

    for namespace in sorted(namespaces):
        post_namespace(env, token, namespace)



def post_namespace(env, token, name_space_name):
    management_zone_name = f'ZZ K8s NS: {name_space_name}'

    management_zone_template = {
     "description": None,
     "dimensionalRules": [],
     "entitySelectorBasedRules": [],
     "metadata": {
      "clusterVersion": "1.240.132.20220503-084001",
      "configurationVersions": [
       0
      ]
     },
     "name": "{{.name}}",
     "rules": [
      {
       "conditions": [
        {
         "comparisonInfo": {
          "negate": False,
          "operator": "EQUALS",
          "type": "TAG",
          "value": {
           "context": "CONTEXTLESS",
           "key": "Kubernetes Namespace",
           "value": "{{.namespace}}"
          }
         },
         "key": {
          "attribute": "PROCESS_GROUP_TAGS",
          "type": "STATIC"
         }
        }
       ],
       "enabled": True,
       "propagationTypes": [
        "PROCESS_GROUP_TO_HOST",
        "PROCESS_GROUP_TO_SERVICE"
       ],
       "type": "PROCESS_GROUP"
      }
     ]
    }

    management_zone = copy.deepcopy(management_zone_template)
    management_zone['name'] = management_zone_name
    management_zone['rules'][0]['conditions'][0]['comparisonInfo']['value']['value'] = name_space_name

    endpoint = '/api/config/v1/managementZones'
    post(env, token, endpoint, json.dumps(management_zone))


def post(env, token, endpoint, payload):
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})

        if r.status_code == 201:
            management_zone_id = r.json().get('id')
            management_zone_name = r.json().get('name')
            print(f'Created management zone: "{management_zone_name}" ({management_zone_id}) at endpoint "{endpoint}"')
        else:
            error_filename = '$post_error_payload.json'
            with open(error_filename, 'w') as file:
                file.write(formatted_payload)
                name = json_data.get('name')
                if name:
                    print('Name: ' + name)
                print('Error in "post(env, token, endpoint, payload)" method')
                print('See ' + error_filename + ' for more details')
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
            exit(get_line_number())
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def delete_kubernetes_namespace_management_zones(env_name, env, token):
    # Safety Check
    if env_name != 'Personal':
        print('Error in "delete_kubernetes_namespace_management_zones()" method')
        print('Not for use in this environment')
        print('Env: ' + env)
        print('Exit code shown below is the source code line number of the exit statement invoked')
        exit(get_line_number())

    endpoint = '/api/config/v1/managementZones'
    raw_params = 'pageSize=1000'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    management_zone_json_list = dynatrace_api.get(env, token, endpoint, params)

    print(management_zone_json_list)

    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            management_zone_id = inner_management_zone_json.get('id')
            management_zone_name = inner_management_zone_json.get('name')
            if management_zone_name.startswith('ZZ K8s NS'):
                print(f'{management_zone_name} ({management_zone_id})')
                delete(env, token, endpoint, management_zone_id)


def delete(env, token, endpoint, object_id):
    url = env + endpoint + '/' + object_id
    try:
        r: Response = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        if r.status_code == 204:
            print('Deleted ' + object_id + ' (' + endpoint + ')')
        else:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
        if r.status_code not in [200, 201, 204]:
            # print(json_data)
            print('Error in "delete(endpoint, object_id)" method')
            print('Env: ' + env)
            print('Endpoint: ' + endpoint)
            print('Token: ' + token)
            print('Object ID: ' + object_id)
            print('Exit code shown below is the source code line number of the exit statement invoked')
        return r
    except ssl.SSLError:
        print('SSL Error')
        exit(get_line_number())


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def run():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    print('Generate kubernetes management zones by namespace')

    # delete_kubernetes_namespace_management_zones(env_name, env, token)

    process(env, token)


if __name__ == '__main__':
    run()
