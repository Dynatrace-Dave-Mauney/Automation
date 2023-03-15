import json
import requests
import ssl
import sys
import time
import urllib.parse
from inspect import currentframe
from requests import Response

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    check_disk_space(env, token)


def check_disk_space(env, token):
    metric_friendly_name = 'Disk Space Usage'
    threshold = 99
    # metric_selector = '(100*(builtin:host.disk.avail)/(builtin:host.disk.free):splitBy():sort(value(auto,descending))):fold:limit(20):filter(series(avg,gt(1000000000000)))'
    metric_selector = f'builtin:host.disk.free:fold:filter(series(avg,gt({threshold}))):splitBy("dt.entity.host"):sort(value(auto,descending))'
    entity_selector = 'type(HOST)'
    from_time = 'now-30m'

    check_metric(env, token, metric_friendly_name, metric_selector, entity_selector, from_time, threshold)


def check_metric(env, token, metric_friendly_name, metric_selector, entity_selector, from_time, threshold):
    endpoint = '/api/v2/metrics/query'
    params = 'metricSelector=' + urllib.parse.quote(metric_selector) + '&from=' + from_time + '&entitySelector=' + urllib.parse.quote(entity_selector)
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(metrics_json_list)
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        for result in result_list:
            # metric_id = result.get('metricId')
            data = result.get('data')
            for datapoint in data:
                host_id = datapoint.get("dimensionMap").get("dt.entity.host").strip()
                display_name = f'{metric_friendly_name} on {host_id}'
                # print(datapoint)
                # display_name = datapoint.get('dimensionMap').get('dt.entity.host_name').strip()
                value = datapoint.get('values')[0]
                if value:
                    print(display_name + '|' + str(value))

                    # TODO: Remove test filters
                    host_filter = 'HOST-B1854D399E4037C6'
                    # if value > threshold:

                    if value > threshold and host_id == host_filter:
                        print(f'Posting a resource event because {int(value)} is greater than the threshold of {threshold}')
                        post_resource_contention_event(env, token, metric_friendly_name, host_id, value, threshold)


def post_resource_contention_event(env, token, metric_friendly_name, host_id, value, threshold):
    event_type = 'RESOURCE_CONTENTION_EVENT'
    start_time = get_current_time_as_epoch_in_milliseconds()
    end_time = get_current_time_as_epoch_in_milliseconds() + 5
    timeout = 0
    host = get_host(env, token, host_id)
    host_name = host.get('displayName')
    entity_selector = f'entityId({host_id})'
    properties = {f'Metric ({metric_friendly_name})': value, f'Metric Threshold ({metric_friendly_name})': threshold, 'Host Id': host_id, 'Host Name': host_name}
    title = f'{metric_friendly_name} too high'
    post_event(env, token, event_type, title, start_time, end_time, timeout, entity_selector, properties)


def post_event(env, token, event_type, title, start_time, end_time, timeout, entity_selector, properties):
    payload = {"eventType": event_type, "title": title, "startTime": start_time, "endTime": end_time, "timeout": timeout, "entitySelector": entity_selector, "properties": properties}
    post(env, token, '/api/v2/events/ingest', json.dumps(payload))


def post(env, token, endpoint: str, payload: str) -> Response:
    # In general, avoid post in favor of put so "fixed ids" can be used
    json_data = json.loads(payload)
    formatted_payload = json.dumps(json_data, indent=4, sort_keys=False)
    url = env + endpoint
    try:
        r: Response = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        print('Status Code: %d' % r.status_code)
        print('Reason: %s' % r.reason)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 201, 204]:
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


def get_host(env, token, host_id):
    headers = {'Authorization': 'Api-Token ' + token}
    endpoint = f'api/v1/entity/infrastructure/hosts/{host_id}'

    try:
        url = f'{env}/{endpoint}'
        r = requests.get(url, headers=headers)
        # entity_content = json.dumps(r.json(), indent=4)
        if r.status_code == 200:
            # print(json.dumps(r.json(), indent=4))
            # return r.json().get('discoveredName')
            # return r.json().get('metadata').get('pluginMetadata').get('Queue manager')
            return r.json()
        else:
            if r.status_code == 404:
                if "The given entity id is not assigned to an entity" in r.text:
                    print(f'Process Group Instance ID {host_id} not found on this tenant')
            else:
                print('Status Code: %d' % r.status_code)
                print('Reason: %s' % r.reason)
                if len(r.text) > 0:
                    print(r.text)
    except ssl.SSLError:
        print("SSL Error")


def get_current_time_as_epoch_in_milliseconds():
    milliseconds = time.time_ns() // 1000000
    return milliseconds


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def run():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token)


def main(arguments):
    usage = '''
    generic_metric_alerting.py: Query a metric 

    Usage:    generic_metric_alerting.py <tenant/environment URL> <token>
    Examples: generic_metric_alerting.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              generic_metric_alerting.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
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
