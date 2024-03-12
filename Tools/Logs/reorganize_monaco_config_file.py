# Reorder the YAML contents to the desired rule order
# Note: Any rules not present in "desired_rule_order" will be dropped from config.yaml

# import copy
import yaml


INPUT_PATH = '/Dynatrace/Customers/ODFL/LogIngestionRules/Repo'
INPUT_PATH = 'C:\\Temp\\builtinlogmonitoring.log-storage-settings'

# Lower case environment names!
# env = 'dev'
env = 'preprod'
# env = 'prod'

dev_desired_rule_order = [
    'Exclude_log_source__Rapid7_',
    'Exclude_log_content__GET__index.html__for_process_technology__Nginx_',
    'Exclude_log_content__Hibernate_statements_',
    'Exclude_log_content__kube-probe_health_check_requests_',
    'Exclude_log_content__actuator_health_',
    'Exclude_log_record_level_DEBUG_or_INFO',
    'Exclude_log_content_FINE,_TRACE,_INFO_or_DEBUG',
    'Include_k8s_namespaces',
    'Include_log_content__Jboss_server_started_with_errors_',
]
preprod_desired_rule_order = [
    'Exclude_log_source__Rapid7_',
    'Exclude_log_content__GET__index.html__for_process_technology__Nginx_',
    'Exclude_log_content__Hibernate_statements_',
    'Exclude_log_content__kube-probe_health_check_requests_',
    'Exclude_log_content__actuator_health_',
    'Include_k8s_namespace__weight-inspection_namespace__containers_log_content_ERROR_or_WARN_or_INFO',
    'Include_k8s_namespace__common__container__email-service__log_record_level_ERROR_or_WARN',
    'Include_k8s_namespace__billing__container__bol-core_',
    'Include_k8s_namespace__freight-imaging__containers',
    'Include_k8s_namespace__pickup__container__pickup-service_',
    'Include_k8s_namespace__track-trace-api__container__track-trace-external-api_',
    'Exclude_log_record_level_DEBUG_or_INFO',
    'Exclude_log_content_FINE,_TRACE,_INFO_or_DEBUG',
    'Include_k8s_namespaces',
    'Include_log_content__Jboss_server_started_with_errors_',
]

prod_desired_rule_order = [
    'Exclude_log_source__Rapid7_',
    'Exclude_log_content__GET__index.html__for_process_technology__Nginx_',
    'Exclude_log_content__Hibernate_statements_',
    'Exclude_log_content__kube-probe_health_check_requests_',
    'Exclude_log_content__actuator_health_',
    'Include_k8s_namespace__weight-inspection_namespace__containers_log_content_ERROR_or_WARN_or_INFO',
    'Include_k8s_namespace__common__container__email-service__log_record_level_ERROR_or_WARN',
    'Include_k8s_namespace__billing__container__bol-core_',
    'Include_k8s_namespace__freight-imaging__containers',
    'Include_k8s_namespace__pickup__container__pickup-service_',
    'Include_k8s_namespace__track-trace-api__container__track-trace-external-api_',
    'Exclude_log_record_level_DEBUG_or_INFO',
    'Exclude_log_content_FINE,_TRACE,_INFO_or_DEBUG',
    'Include_k8s_namespaces',
    'Include_log_source__Salesforce_feed_upload_',
    'Include_log_source__Truckload-rate-app__log_content__notifyExtol_Exception_',
    'Include_log_source__fuel-surcharge-batch-process-app.log__log_content__ERROR__(Fuel_PricingRating)',
    'Include_log_content__Jboss_server_started_with_errors_',
    'Include_log_content__previous_execution_of_timer___(Salesforce_feed.ear)',
]


def reorder_config_file_rules():
    config_file_name = f'{INPUT_PATH}/config.yaml'
    yaml_dict = read_yaml(config_file_name)
    configs = yaml_dict.get('configs')

    config_lookup = {}
    new_configs = []

    print(f'Environment: {env}')
    if env == 'dev':
        desired_rule_order = dev_desired_rule_order
    else:
        if env == 'preprod':
            desired_rule_order = preprod_desired_rule_order
        else:
            desired_rule_order = prod_desired_rule_order

    for config in configs:
        if config:
            monaco_id = config.get('id')
            config_lookup[monaco_id] = config

    # print(config_lookup)

    for ordered_id in desired_rule_order:
        config = config_lookup.get(ordered_id)
        if config:
            new_configs.append(config)

    yaml_dict['configs'] = new_configs
    write_yaml(yaml_dict, config_file_name)


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def write_yaml(any_dict, filename):
    with open(filename, 'w') as file:
        yaml.dump(any_dict, file, sort_keys=False)


def main():
    reorder_config_file_rules()


if __name__ == '__main__':
    main()
