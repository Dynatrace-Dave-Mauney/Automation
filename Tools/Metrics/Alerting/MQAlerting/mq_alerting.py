import json
import sys
import time
import urllib.parse
import yaml
from inspect import currentframe
from requests import Response

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    check_oldest_message_age(env, token)
    check_depth(env, token)
    check_depth_percentage(env, token)


def check_oldest_message_age(env, token):
    yaml_dict = read_yaml('oldest_message.yaml')
    metric_friendly_name = 'Oldest Message Age'
    metric_selector_schema_id = 'ext:tech.IBMMQ_OneAgent.Queue.OldestMessageAge'
    metric_selector_transformation = ':fold:sort(dimension("Queue",ascending))'
    from_time = 'now-30m'
    check_mq_metric(env, token, metric_friendly_name, metric_selector_schema_id, metric_selector_transformation, from_time, yaml_dict)


def check_depth_percentage(env, token):
    yaml_dict = read_yaml('queue_depth_pct.yaml')
    metric_friendly_name = 'Queue Depth Percentage'
    metric_selector_schema_id = 'ext:tech.IBMMQ_OneAgent.Queue.PercentQueueDepth'
    metric_selector_transformation = ':fold:sort(dimension("Queue",ascending))'
    from_time = 'now-30m'
    check_mq_metric(env, token, metric_friendly_name, metric_selector_schema_id, metric_selector_transformation, from_time, yaml_dict)


def check_depth(env, token):
    yaml_dict = read_yaml('queue_depth.yaml')
    metric_friendly_name = 'Queue Depth'
    metric_selector_schema_id = 'ext:tech.IBMMQ_OneAgent.Queue.Depth'
    metric_selector_transformation = ':fold:sort(dimension("Queue",ascending))'
    from_time = 'now-30m'
    check_mq_metric(env, token, metric_friendly_name, metric_selector_schema_id, metric_selector_transformation, from_time, yaml_dict)


def check_mq_metric(env, token, metric_friendly_name, metric_selector_schema_id, metric_selector_transformation, from_time, yaml_dict):
    endpoint = '/api/v2/metrics/query'
    entity_selector = 'type(PROCESS_GROUP_INSTANCE)'
    params = 'metricSelector=' + urllib.parse.quote(metric_selector_schema_id) + metric_selector_transformation + '&from=' + from_time + '&entitySelector=' + urllib.parse.quote(entity_selector)
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, params=params)
    metrics_json_list = r.json()
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        if result_list:
            for result in result_list:
                # metric_id = result.get('metricId')
                data = result.get('data')
                for datapoint in data:
                    'dt.entity.process_group_instance'
                    queue_name = datapoint.get("dimensionMap").get("Queue").strip()

                    alert_list = yaml_dict.get(queue_name)

                    if not alert_list:
                        # print(f'Queue {queue_name} has no alerting set up')
                        continue

                    process_group_instance_id = datapoint.get("dimensionMap").get("dt.entity.process_group_instance").strip()
                    # display_name = f'{queue_name} on {process_group_instance_id}'
                    # print(f'Queue Manager: {queue_manager}')
                    # print(datapoint)
                    # display_name = datapoint.get('dimensionMap').get('dt.entity.process_group_instance_name').strip()
                    value = datapoint.get('values')[0]
                    # if value > 0:
                    #     print(f'{display_name}|{metric_friendly_name}|{value}')

                    # Testing: use filters to limit number of problems raised
                    # pgi_filter = 'PROCESS_GROUP_INSTANCE-62818F438145AA20'
                    # queue_filter = 'SYSTEM.AUTH.DATA.QUEUE'
                    # if value > lower_threshold and process_group_instance_id == pgi_filter and queue_name == queue_filter:

                    for alert in alert_list:
                        lower_threshold = alert.get('lower')
                        upper_threshold = alert.get('upper')
                        thresholds = alert.get('thresholds')
                        # print(queue_name, lower_threshold, alert)
                        if thresholds:
                            for threshold in thresholds:
                                if value > float(threshold):
                                    print(f'Posting a resource event for {queue_name} because {metric_friendly_name} value of {int(value)} is greater than the threshold of {threshold}')
                                    post_resource_contention_event(env, token, metric_friendly_name, queue_name, process_group_instance_id, value, threshold, alert)
                        else:
                            if lower_threshold and upper_threshold and float(upper_threshold) > 0:
                                if float(lower_threshold) < value < float(upper_threshold):
                                    print(f'Posting a resource event for {queue_name} because {metric_friendly_name} value of {int(value)} is greater than the lower threshold of {lower_threshold} and less than the upper threshold of {upper_threshold}')
                                    post_resource_contention_event(env, token, metric_friendly_name, queue_name, process_group_instance_id, value, lower_threshold, alert)
                            else:
                                if lower_threshold and value > float(lower_threshold):
                                    print(f'Posting a resource event for {queue_name} because {metric_friendly_name} value of {int(value)} is greater than the threshold of {lower_threshold}')
                                    post_resource_contention_event(env, token, metric_friendly_name, queue_name, process_group_instance_id, value, lower_threshold, alert)


def post_resource_contention_event(env, token, metric_friendly_name, queue_name, process_group_instance_id, value, threshold, alert):
    event_type = 'RESOURCE_CONTENTION_EVENT'
    start_time = get_current_time_as_epoch_in_milliseconds()
    end_time = get_current_time_as_epoch_in_milliseconds() + 5
    timeout = 0
    process_group_instance = get_process_group_instance(env, token, process_group_instance_id)
    queue_manager = process_group_instance.get('metadata').get('pluginMetadata').get('Queue manager')
    process_group_instance_name = process_group_instance.get('displayName')
    entity_selector = f'entityId({process_group_instance_id})'
    msg = alert.get('msg', ' ')
    notify = alert.get('notify', ' ')
    distribution = alert.get('distribution', ' ')
    lower = alert.get('lower', ' ')
    upper = alert.get('upper', ' ')
    properties = {'Queue Manager': queue_manager, 'Queue': queue_name, f'Metric ({metric_friendly_name})': value, f'Metric Threshold ({metric_friendly_name})': threshold, 'Process Group Instance Id': process_group_instance_id, 'Process Group Instance Name': process_group_instance_name, 'msg': msg, 'notify': notify, 'distribution': distribution, 'lower': lower, 'upper': upper}
    title = f'{metric_friendly_name} for {queue_name} too high'

    # Testing:
    # print('DEBUG:', env, token, event_type, title, start_time, end_time, timeout, entity_selector, properties)
    # return

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


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


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
    mq_alerting.py: Query a metric 

    Usage:    mq_alerting.py <tenant/environment URL> <token>
    Examples: mq_alerting.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              mq_alerting.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
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
