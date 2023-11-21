import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def test_get_object_list(env, token, endpoint):
    r = dynatrace_api.get_object_list(env, token, endpoint)
    return r


def test_get_alerting_profiles(env, token):
    endpoint = '/api/config/v1/alertingProfiles'
    params = ''
    r = dynatrace_api.get(env, token, endpoint, params)
    return r


def test_get_metrics(env, token):
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    r = dynatrace_api.get(env, token, endpoint, params)
    return r


def test_get_entity_types(env, token):
    endpoint = '/api/v2/entityTypes'
    raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    r = dynatrace_api.get(env, token, endpoint, params)
    return r


def test_get_entity_type_host(env, token):
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=500&entitySelector=type(HOST)&fields=+properties.monitoringMode, +properties.state,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    r = dynatrace_api.get(env, token, endpoint, params)
    return r


def test_post(env, token, endpoint, payload):
    r = dynatrace_api.post(env, token, endpoint, payload)
    return r


def test_post_plain_text(env, token, endpoint, payload):
    r = dynatrace_api.post_plain_text(env, token, endpoint, payload)
    return r


def test_put(env, token, endpoint, object_id, payload):
    r = dynatrace_api.put(env, token, endpoint, object_id, payload)
    return r


def test_delete(env, token, endpoint, object_id):
    dynatrace_api.delete(env, token, endpoint, object_id)


def main():
    _, env, token = environment.get_environment('Personal')

    endpoint = '/api/config/v1/autoTags'
    r = test_get_object_list(env, token, endpoint)
    # object_json_list = json.loads(r.text).get('values')
    if r.status_code != 200:
        print(f'Unexpected status code {r.status_code} from "test_get_object_list" method for endpoint "{endpoint}"')
        print_response_details(r)
        exit(1)

    # print(f'Result successfully obtained for endpoint "{endpoint}" from "test_get_object_list" method: {object_json_list}')
    print(f'Result successfully obtained for endpoint "{endpoint}" from "test_get_object_list" method')

    alerting_profiles_list = test_get_alerting_profiles(env, token)
    # print(f'Result successfully obtained from "test_get_alerting_profiles" method: {alerting_profiles_list}')
    print(f'Result successfully obtained from "test_get_alerting_profiles" method')

    metrics_list = test_get_metrics(env, token)
    # print(f'Result successfully obtained from "test_get_metrics" method: {metrics_list}')
    print(f'Result successfully obtained from "test_get_metrics" method')

    entity_type_list = test_get_entity_types(env, token)
    # print(f'Result successfully obtained from "test_get_entity_types" method: {entity_type_list}')
    print(f'Result successfully obtained from "test_get_entity_types" method')

    host_list = test_get_entity_type_host(env, token)
    # print(f'Result successfully obtained from "test_get_entity_type_host" method: {host_list}')
    print(f'Result successfully obtained from "test_get_entity_type_host" method')

    endpoint = '/api/config/v1/autoTags'
    payload = json.dumps({'name': 'TestAutoTag', 'rules': []})

    r = test_post(env, token, endpoint, payload)
    if r.status_code != 201:
        print('Unexpected status code from "test_post" method')
        print_response_details(r)
        exit(1)

    object_id = json.loads(r.text).get('id')
    print(f'Posted {object_id} successfully with "test_post" method')

    r = test_put(env, token, endpoint, object_id, payload)
    if r.status_code != 204:
        print('Unexpected status code from "test_put" method')
        print_response_details(r)
        exit(1)

    print(f'Put {object_id} successfully with "test_put" method')

    test_delete(env, token, endpoint, object_id)
    print(f'Deleted {object_id} successfully with "test_delete" method')

    endpoint = '/api/v2/metrics/ingest'
    payload = 'com.dynatrace.automation.responseTime,language=python 1000'

    r = test_post_plain_text(env, token, endpoint, payload)
    if r.status_code != 202:
        print('Unexpected status code {r.status_code} from "test_post_plain_text" method')
        print_response_details(r)
        exit(1)

    print(f'Posted plain text object successfully')

    print('End of sunny day tests...')
    print('')

    # print('Begin failure testing...')
    # Must test one at a time since a failure generally results in an exit statement from dynatrace_api.py
    # Test bad endpoint for get
    # dynatrace_api.get(env, token, '/api/v2/metrics/BAD', None)
    # Test bad endpoint for get object list
    # test_get_object_list(env, token, '/api/config/v1/BAD')
    # Test bad endpoint for delete
    # test_delete(env, token, '/api/v2/bad/endpoint', 'BAD-OBJECT-ID')


def print_response_details(r):
    print(r)
    print(r.status_code)
    print(r.text)
    print(r.reason)
    print(r.url)
    print(r.headers)
    print(r.raw)


if __name__ == '__main__':
    main()
