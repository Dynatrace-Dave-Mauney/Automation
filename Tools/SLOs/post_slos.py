"""

POST SLOs based on a template, changing the following fields per SLO:

    summary
    searchSummary
    author
    name
    metricName
    metricExpression
    filter

"""

import json

from Reuse import directories_and_files
from Reuse import dynatrace_api
from Reuse import environment


def process():
    target_env_name = 'Personal'
    # target_env_name = 'Upper'

    # Fake examples
    management_zone_name_list = [
        'App: KEEP - PROD',
        # 'FAKE1-PERSONAL',
        # 'FAKE2-PERSONAL',
    ]

    for management_zone_name in management_zone_name_list:
        post_http_check_availability_slo(target_env_name, management_zone_name)
        post_browser_availability_slo(target_env_name, management_zone_name)
        post_service_slo(target_env_name, management_zone_name)
        post_host_slo(target_env_name, management_zone_name)

def post_http_check_availability_slo(target_env_name, management_zone_name):
    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')
    monitor_type = 'Synthetic Availability (HTTP)'
    summary = f'{management_zone_name} - {monitor_type}'
    author = 'Dynatrace support user #262974423'
    metric_name = f'{management_zone_name_clean.lower().replace("-", "_")}_synthetic_availability'
    metric_expression = 'builtin:synthetic.http.availability.location.total:splitBy()'
    slo_filter = f'type(HTTP_CHECK), mzName({management_zone_name})'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)


def post_browser_availability_slo(target_env_name, management_zone_name):
    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')
    monitor_type = 'Synthetic Availability (Browser)'
    summary = f'{management_zone_name} - {monitor_type}'
    author = 'Dynatrace support user #262974423'
    metric_name = f'{management_zone_name_clean.lower().replace("-", "_")}_synthetic_browser_availability'
    metric_expression = 'builtin:synthetic.browser.availability.location.total:splitBy()'
    slo_filter = f'type(SYNTHETIC_TEST), mzName({management_zone_name})'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)


def post_service_slo(target_env_name, management_zone_name):
    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')
    author = 'Dynatrace support user #262974423'
    slo_filter = f'type(SERVICE), mzName({management_zone_name})'
    summary = f'{management_zone_name} - Service Errors'
    metric_name = f'{management_zone_name_clean.lower().replace("-", "_")}_service_errors'
    metric_expression = '100-(builtin:service.errors.total.rate:splitby())'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)

    summary = f'{management_zone_name} - Service Performance'
    metric_name = f'{management_zone_name_clean.lower().replace("-", "_")}_service_performance'
    metric_expression = '((builtin:service.response.time:avg:partition("latency",value("good",lt(10000))):splitBy():count:default(0))/(builtin:service.response.time:avg:splitBy():count)*(100))'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)


def post_host_slo(target_env_name, management_zone_name):
    management_zone_name_clean = directories_and_files.get_clean_file_name(management_zone_name, '_').replace(' ', '')
    author = 'Dynatrace support user #262974423'
    slo_filter = f'type(HOST), mzName({management_zone_name})'
    summary = f'{management_zone_name} - Host Availability'
    metric_name = f'{management_zone_name_clean.lower().replace("-", "_")}_host_availability'
    metric_expression = 'builtin:host.availability:avg:setUnit(Percent):splitBy()'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)


def post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter):
    slo = load_slo_template()

    slo['summary'] = summary
    slo['searchSummary'] = summary
    slo['author'] = author
    slo['value']['name'] = summary
    slo['value']['metricName'] = metric_name
    slo['value']['metricExpression'] = metric_expression
    slo['value']['filter'] = slo_filter

    slo_list = [slo]

    env_name, env, token = environment.get_environment_for_function_print_control(target_env_name, friendly_function_name='Dynatrace Automation Tools', print_mode=False)

    endpoint = '/api/v2/settings/objects'
    formatted_slo = json.dumps(slo_list, indent=4, sort_keys=False)

    response = dynatrace_api.post_object(f'{env}{endpoint}', token, formatted_slo)

    # print(f'JSON Response: {response.text}')

    new_object_id = json.loads(response.text)[0].get('objectId')

    print(f'Posted {summary} to {env_name} ({env}) with settings 20 object id {new_object_id}')
    print('')


def load_slo_template():
    with open('standard_slo_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def main():
    process()


if __name__ == '__main__':
    main()
