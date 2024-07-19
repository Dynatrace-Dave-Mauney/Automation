"""

POST key request SLOs based on a template based on configurations.yaml input.

configurations.yaml contents can be generated using "generate_key_request_slos_service_method_list.py"

"""

import json

from Reuse import directories_and_files
from Reuse import dynatrace_api
from Reuse import environment


def process():
    configuration_object = environment.get_configuration_object('configurations.yaml')

    if not configuration_object:
        print('Configuration object ("configuration_object") could not be loaded')
        exit(1)

    target_env_name = environment.get_configuration('target_env_name', configuration_object=configuration_object)
    service_method_list = environment.get_configuration('service_method_list', configuration_object=configuration_object)
    slo_name_prefix = environment.get_configuration('slo_name_prefix', configuration_object=configuration_object)
    slo_evaluation_window = environment.get_configuration('slo_evaluation_window', configuration_object=configuration_object)

    if not target_env_name:
        print('target_env_name could not be loaded')
        exit(1)

    if not service_method_list:
        print('service_method_list could not be loaded')
        exit(1)

    if not slo_name_prefix:
        print('slo_name_prefix could not be loaded')
        exit(1)

    if not slo_evaluation_window:
        print('slo_evaluation_window could not be loaded')
        exit(1)

    print('Current Configuration:')
    print('target_env_name:       ', target_env_name)
    print('service_method_list:   ', service_method_list)
    print('slo_name_prefix:       ', slo_name_prefix)
    print('slo_evaluation_window: ', slo_evaluation_window)

    for service_method in service_method_list:
        post_service_slo(target_env_name, service_method, slo_name_prefix, slo_evaluation_window)


def post_service_slo(target_env_name, service_method, slo_name_prefix, slo_evaluation_window):
    author = 'Dynatrace support user #262974423'
    service_method_name = service_method[0]
    service_method_id = service_method[1]
    slo_filter = f'type("SERVICE_METHOD"), entityId({service_method_id})'
    summary = f'{slo_name_prefix} - {service_method_name}'
    summary_clean = directories_and_files.get_clean_file_name(summary, '_').replace(' ', '').replace('.', '')
    metric_name = f'{summary_clean.lower().replace("-", "_")}'
    metric_expression = 'builtin:service.keyRequest.successes.server.rate'
    post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter, slo_evaluation_window)


def post_slo(target_env_name, summary, author, metric_name, metric_expression, slo_filter, slo_evaluation_window):
    slo = load_slo_template()

    slo['summary'] = summary
    slo['searchSummary'] = summary
    slo['author'] = author
    slo['value']['name'] = summary
    slo['value']['metricName'] = metric_name
    slo['value']['metricExpression'] = metric_expression
    slo['value']['filter'] = slo_filter

    slo['value']['evaluationWindow'] = slo_evaluation_window

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
