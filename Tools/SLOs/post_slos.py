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

from Reuse import dynatrace_api
from Reuse import environment


def process():
    # Fake examples
    asn_list = [
        'FAKE1-PROD',
        'FAKE2-PROD',
    ]

    for asn in asn_list:
        dash_index = asn.find('-') + 1
        env = asn[dash_index:]
        if env == 'PROD':
            target_env_name = 'Prod'
        else:
            if env in ['DEV', 'STG']:
                target_env_name = 'NonProd'
            else:
                if env in ['PERSONAL']:
                    target_env_name = 'Personal'
                else:
                    print('Unsupported target environment!')

        post_default_http_check_availability_slo(target_env_name=target_env_name, monitor_name=asn)
        # post_default_service_slos(target_env_name=target_env_name, asn=asn)


def post_default_service_slos(target_env_name, asn):
    author = 'Dynatrace support user #262974423'
    slo_filter = f'type(SERVICE), mzName({asn})'

    summary = f'{asn} - Service Errors'
    metric_name = f'{asn.lower().replace("-", "_")}_service_errors'
    metric_expression = '100-(builtin:service.errors.total.rate:splitby())'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)

    summary = f'{asn} - Service Performance'
    metric_name = f'{asn.lower().replace("-", "_")}_service_performance'
    metric_expression = '((builtin:service.response.time:avg:partition("latency",value("good",lt(10000))):splitBy():count:default(0))/(builtin:service.response.time:avg:splitBy():count)*(100))'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter)


def post_default_http_check_availability_slo(target_env_name, monitor_name):
    monitor_type = 'Synthetic Availability (HTTP)'
    summary = f'{monitor_name} - {monitor_type}'
    author = 'Dynatrace support user #262974423'
    metric_name = f'{monitor_name.lower().replace("-", "_")}_synthetic_availability'
    metric_expression = 'builtin:synthetic.http.availability.location.total:splitBy()'
    if monitor_name == 'FAKE1-PERSONAL':
        monitor_name = 'ReadOnly'
    slo_filter = f'type(HTTP_CHECK), mzName({monitor_name})'
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
    with open('slo_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def main():
    process()


if __name__ == '__main__':
    main()
