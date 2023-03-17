import copy
import json
import urllib.parse
from inspect import currentframe

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
    dynatrace_api.post(env, token, endpoint, json.dumps(management_zone))


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
                dynatrace_api.delete(env, token, endpoint, management_zone_id)


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

    delete_kubernetes_namespace_management_zones(env_name, env, token)

    # process(env, token)


if __name__ == '__main__':
    run()
