import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def test_get_alerting_profiles(env, token):
    endpoint = '/api/config/v1/alertingProfiles'
    params = ''
    results = dynatrace_api.get(env, token, endpoint, params)
    print(results)


def test_get_metrics(env, token):
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=1000&fields=+displayName,+description,+unit,+aggregationTypes,+defaultAggregation,+dimensionDefinitions,+transformations,+entityType'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    results = dynatrace_api.get(env, token, endpoint, params)
    print(results)


def test_get_entity_types(env, token):
    endpoint = '/api/v2/entityTypes'
    raw_params = 'pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    results = dynatrace_api.get(env, token, endpoint, params)
    print(results)


def test_get_entity_type_host(env, token):
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=500&entitySelector=type(HOST)&fields=+properties.monitoringMode, +properties.state,+toRelationships'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    hosts = dynatrace_api.get(env, token, endpoint, params)
    print(hosts)
    for entities in hosts:
        total_count = int(entities.get('totalCount'))
        if total_count > 0:
            host_entities = entities.get('entities')
            for host in host_entities:
                print(host)


def test_post(env, token):
    endpoint = '/api/config/v1/autoTags'
    payload = json.dumps({'name': 'TestAutoTag', 'rules': []})
    dynatrace_api.post(env, token, endpoint, payload)



def test_post_plain_text(env, token):
    endpoint = '/api/v2/metrics/ingest'
    payload = 'com.dynatrace.automation.responseTime,language=python 1000'
    dynatrace_api.post_plain_text(env, token, endpoint, payload)


def test_put(env, token):
    endpoint = '/api/config/v1/autoTags'
    object_id = 'ab3162ba-71d5-3ceb-b92d-408656024be8'
    payload = json.dumps({'name': 'TestAutoTag', 'rules': []})
    dynatrace_api.put(env, token, endpoint, object_id, payload)


def test_delete(env, token):
    endpoint = '/api/config/v1/autoTags'
    object_id = 'ab3162ba-71d5-3ceb-b92d-408656024be8'
    dynatrace_api.delete(env, token, endpoint, object_id)


def main():
    _, env, token = environment.get_environment('Personal')
    # test_get_alerting_profiles(env, token)
    # test_get_metrics(env, token)
    # test_get_entity_types(env, token)
    # test_get_entity_type_host(env, token)

    # test_post(env, token)
    # test_post_plain_text(env, token)
    # test_put(env, token)
    # test_delete(env, token)


if __name__ == '__main__':
    main()

