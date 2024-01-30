import json
import sys
import time
import urllib.parse

from inspect import currentframe
from requests import Response

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    endpoint = '/api/v2/metrics/query'
    # metric_selector_schema_id = 'builtin:host.availability'
    # metric_selector_transformation = ':names:fold:default(0):sort(dimension("dt.entity.host.name",ascending))'
    # metric_selector_transformation = ':names:fold:default(0)'
    # entity_selector = 'type(HOST)'
    metric_selector_schema_id = 'ext:tech.IBMMQ_OneAgent.Queue.OldestMessageAge'
    metric_selector_transformation = ':fold:sort(dimension("Queue",ascending))'
    entity_selector = 'type(PROCESS_GROUP_INSTANCE)'
    # from_time = 'now-72h'
    from_time = 'now-30m'
    params = 'metricSelector=' + urllib.parse.quote(metric_selector_schema_id) + metric_selector_transformation + '&from=' + from_time + '&entitySelector=' + urllib.parse.quote(entity_selector)
    metrics_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    print(metrics_json_list)
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        for result in result_list:
            # metric_id = result.get('metricId')
            data = result.get('data')
            for datapoint in data:
                'dt.entity.process_group_instance'
                queue_name = datapoint.get("dimensionMap").get("Queue").strip()
                process_group_instance_id = datapoint.get("dimensionMap").get("dt.entity.process_group_instance").strip()
                display_name = f'{queue_name} on {process_group_instance_id}'
                # print(f'Queue Manager: {queue_manager}')
                # print(datapoint)
                # display_name = datapoint.get('dimensionMap').get('dt.entity.process_group_instance_name').strip()
                value = datapoint.get('values')[0]
                if value > 0:
                    print(display_name + '|' + str(value))
                threshold = 1200
                # TODO: Remove test filters
                pgi_filter = 'PROCESS_GROUP_INSTANCE-62818F438145AA20'
                queue_filter = 'SYSTEM.AUTH.DATA.QUEUE'
                # if value > threshold:
                if value > threshold and process_group_instance_id == pgi_filter and queue_name == queue_filter:
                    print(f'Posting a resource event because {int(value)} is greater than the threshold of {threshold}')
                    post_resource_contention_event(env, token, queue_name, process_group_instance_id, value, threshold)
                # print(str(values))


def post_resource_contention_event(env, token, queue_name, process_group_instance_id, value, threshold):
    event_type = 'RESOURCE_CONTENTION_EVENT'
    start_time = get_current_time_as_epoch_in_milliseconds()
    end_time = get_current_time_as_epoch_in_milliseconds() + 5
    timeout = 0
    # entity_selector = None
    process_group_instance = get_process_group_instance(env, token, process_group_instance_id)
    queue_manager = process_group_instance.get('metadata').get('pluginMetadata').get('Queue manager')
    process_group_instance_name = process_group_instance.get('displayName')
    entity_selector = f'entityId({process_group_instance_id})'
    properties = {'Queue Manager': queue_manager, 'Queue': queue_name, 'Oldest Message Age': value, 'Threshold': threshold, 'Process Group Instance Id': process_group_instance_id, 'Process Group Instance Name': process_group_instance_name}
    title = f'Oldest Message Age for {queue_name} too high'
    post_event(env, token, event_type, title, start_time, end_time, timeout, entity_selector, properties)


def post_event(env, token, event_type, title, start_time, end_time, timeout, entity_selector, properties):
    payload = {"eventType": event_type, "title": title, "startTime": start_time, "endTime": end_time, "timeout": timeout, "entitySelector": entity_selector, "properties": properties}
    post(env, token, '/api/v2/events/ingest', json.dumps(payload))


def post(env, token, endpoint: str, payload: str) -> Response:
    return dynatrace_api.post_object(f'{env}{endpoint}', token, payload)


def get_process_group_instance(env, token, process_group_instance_id):
    endpoint = f'/api/v1/entity/infrastructure/processes'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{process_group_instance_id}', token)
    return r.json()


def get_current_time_as_epoch_in_milliseconds():
    milliseconds = time.time_ns() // 1000000
    return milliseconds


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def run():
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


def main(arguments):
    usage = '''
    query_metric.py: Query a metric 

    Usage:    query_metric.py <tenant/environment URL> <token>
    Examples: query_metric.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              query_metric.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
    '''

    # print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 2:
        print(usage)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments[1], arguments[2])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
