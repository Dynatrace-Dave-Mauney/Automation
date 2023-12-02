import json
import time
import urllib.parse

from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from Reuse import dynatrace_api
from Reuse import environment

auto_tags_endpoint = '/api/config/v1/autoTags'
alerting_profiles_endpoint = '/api/config/v1/alertingProfiles'
metrics_endpoint = '/api/v2/metrics'
entity_types_endpoint = '/api/v2/entityTypes'
entities_endpoint = '/api/v2/entities'


def test_get_alerting_profiles(env, token):
    return dynatrace_api.get_json_list_with_pagination(f'{env}{alerting_profiles_endpoint}', token)


def test_get_metrics(env, token):
    raw_params = 'pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    return dynatrace_api.get_json_list_with_pagination(f'{env}{metrics_endpoint}', token, params=params)


def test_get_entity_types(env, token):
    raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    return dynatrace_api.get_json_list_with_pagination(f'{env}{entity_types_endpoint}', token, params=params)


def test_get_entity_type_host(env, token):
    raw_params = 'pageSize=500&entitySelector=type(HOST)&fields=+properties.monitoringMode, +properties.state,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    return dynatrace_api.get_json_list_with_pagination(f'{env}{entities_endpoint}', token, params=params)


def test_get_without_pagination(url, token, **kwargs):
    return dynatrace_api.get_without_pagination(url, token, **kwargs)


def test_post_object(url, token, payload, **kwargs):
    return dynatrace_api.post_object(url, token, payload, **kwargs)


def test_post_plain_text(env, token, payload):
    return dynatrace_api.post_plain_text(env, token, payload)


def test_put_object(url, token, payload):
    return dynatrace_api.put_object(url, token, payload)


def test_delete_object(url, token):
    dynatrace_api.delete_object(url, token)


def main():
    _, env, token = environment.get_environment('Personal')

    print('')
    print('Test Dynatrace API')
    print('')
    print('Start sunny day tests...')
    # alerting_profiles_list = test_get_alerting_profiles(env, token)
    alerting_profiles_list = test_get_alerting_profiles(env, token)
    print(f'PASS: Result successfully obtained from "test_get_alerting_profiles" method: {len(alerting_profiles_list)} alerting profile pages')
    # print('PASS: Result successfully obtained from "test_get_alerting_profiles" method')

    metrics_list = test_get_metrics(env, token)
    print(f'PASS: Result successfully obtained from "test_get_metrics" method: {len(metrics_list)} metrics pages')
    # print('PASS: Result successfully obtained from "test_get_metrics" method')

    entity_type_list = test_get_entity_types(env, token)
    print(f'PASS: Result successfully obtained from "test_get_entity_types" method: {len(entity_type_list)} entity pages')
    # print('PASS: Result successfully obtained from "test_get_entity_types" method')

    host_list = test_get_entity_type_host(env, token)
    print(f'PASS: Result successfully obtained from "test_get_entity_type_host" method: {len(host_list)} host pages')
    # print('PASS: Result successfully obtained from "test_get_entity_type_host" method')

    # params = ''
    # headers = {'Authorization': "Api-Token " + token}
    # timeout = 60
    # verify = True
    # disable_verify_warnings = False
    # handle_exceptions = True
    exit_on_exception = False
    r = test_get_without_pagination(f'{env}{auto_tags_endpoint}', token, exit_on_exception=exit_on_exception)
    if r.status_code == 200:
        results = json.loads(r.text)
        print(f'PASS: Result successfully obtained from "test_get_without_pagination" method: {len(results)} objects for endpoint {auto_tags_endpoint}')
    else:
        print(f'FAIL: Unexpected status code {r.status_code} from "test_get_without_pagination" method for endpoint "{auto_tags_endpoint}"')
        print_response_details(r)

    object_json_list = json.loads(r.text).get('values')
    print(f'PASS: Result successfully obtained for endpoint "{auto_tags_endpoint}" from "test_get_without_pagination" method: {object_json_list}')
    # print('PASS: Result successfully obtained for endpoint from "test_get_without_pagination" method')

    payload = json.dumps({'name': 'TestAutoTag', 'rules': []})

    r = test_post_object(f'{env}{auto_tags_endpoint}', token, payload)
    if r.status_code != 201:
        print('FAIL: Unexpected status code from "test_post_object" method')
        print_response_details(r)

    object_id = json.loads(r.text).get('id')
    print(f'PASS: Posted {object_id} successfully with "test_post_object" method')

    r = test_put_object(f'{env}{auto_tags_endpoint}/{object_id}', token, payload)
    if r.status_code != 204:
        print('FAIL: Unexpected status code from "test_put_object" method')
        print_response_details(r)

    print(f'PASS: Put {object_id} successfully with "test_put_object" method')

    test_delete_object(f'{env}{auto_tags_endpoint}/{object_id}', token)
    print(f'PASS: Deleted {object_id} successfully with "test_delete_object" method')
    sleep(5)

    r = test_post_object(f'{env}{auto_tags_endpoint}', token, payload)
    if r.status_code != 201:
        print('FAIL: Unexpected status code from "test_post_object" method')
        print_response_details(r)

    object_id = json.loads(r.text).get('id')
    print(f'PASS: Posted {object_id} successfully with "test_post_object" method')

    # Save some information for rainy day test of double post
    sunny_day_post_object_id = object_id
    sunny_day_post_payload = payload

    endpoint = '/api/v2/metrics/ingest'
    payload = 'com.dynatrace.automation.responseTime,language=python 1000'

    r = test_post_plain_text(f'{env}{endpoint}', token, payload)
    if r.status_code != 202:
        print('FAIL: Unexpected status code {r.status_code} from "test_post_plain_text" method')
        print_response_details(r)

    print(f'PASS: Posted plain text object successfully')

    print('End sunny day tests...')
    print('')

    print('Begin rainy day tests...')
    # Double post for error handling testing
    try:
        # r = test_post_object(f'{env}{endpoint}', token, payload)
        r = test_post_object(f'{env}{auto_tags_endpoint}', token, sunny_day_post_payload, handle_exceptions=False, exit_on_exception=False)
        print(f'FAIL: Double post worked unexpectedly!')
        print_response_details(r)
    except HTTPError:
        print('PASS: Double post got expected HTTPError exception')

    # Cleanup
    test_delete_object(f'{env}{auto_tags_endpoint}/{sunny_day_post_object_id}', token)

    # Test bad endpoint for gets with no exception handling
    try:
        dynatrace_api.get_json_list_with_pagination(f'{env}/api/v1/bad/endpoint', token, handle_exceptions=False)
        print('FAIL: get_json_list_with_pagination with bad endpoint did not get expected exception')
    except RequestException:
        print('PASS: get_json_list_with_pagination with bad endpoint got expected exception')

    try:
        dynatrace_api.get_without_pagination(f'{env}/api/v1/bad/endpoint', token, handle_exceptions=False)
        print('FAIL: get_without_pagination with bad endpoint did not get expected exception')
    except RequestException:
        print('PASS: get_without_pagination with bad endpoint got expected exception')

    # Test bad endpoint for delete
    try:
        dynatrace_api.delete_object(f'{env}/api/v1/bad/endpoint', token, handle_exceptions=False)
        print('FAIL: delete_object with bad endpoint did not get expected exception')
    except RequestException:
        print('PASS: delete_object with bad endpoint got expected exception')

    print('End rainy day tests...')


def print_response_details(r):
    print(r)
    print(r.status_code)
    print(r.text)
    print(r.reason)
    print(r.url)
    print(r.headers)
    print(r.raw)


def sleep(seconds):
    print(f'Sleeping for {seconds} seconds to allow for eventual consistency')
    time.sleep(seconds)


if __name__ == '__main__':
    main()
