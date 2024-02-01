# import copy
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

entity_types_of_interest = [
    'APPLICATION',
    'CLOUD_APPLICATION',
    # 'CLOUD_APPLICATION_INSTANCE',
    'CLOUD_APPLICATION_NAMESPACE',
    'CONTAINER_GROUP',
    # 'CONTAINER_GROUP_INSTANCE',
    # 'DATABASE_SERVICE',
    'HOST',
    'KUBERNETES_CLUSTER',
    'KUBERNETES_NODE',
    'KUBERNETES_SERVICE',
    'PROCESS_GROUP',
    # 'PROCESS_GROUP_INSTANCE',
    'SERVICE',
]

openshift_admin_ignore_list = [
    'CLOUD_APPLICATION',
    'CONTAINER_GROUP',
    'PROCESS_GROUP',
]


def process(env, token):
    rows = []
    for entity_type in entity_types_of_interest:
        endpoint = '/api/v2/entities'
        entity_selector = 'type(' + entity_type + ')'
        raw_params = f'&entitySelector={entity_selector}&fields=managementZones'
        if entity_type == 'SERVICE':
            raw_params += ',properties.serviceType'
        params = urllib.parse.quote(raw_params, safe='/,&=')
        entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
        for entities_json in entities_json_list:
            inner_entities_json_list = entities_json.get('entities')
            for inner_entities_json in inner_entities_json_list:
                entity_display_name = inner_entities_json.get('displayName')
                if entity_type.startswith('PROCESS_GROUP'):
                    # Skip the "Dynatrace Internal" process group/process group instances
                    if entity_display_name.startswith('Dynatrace') or entity_display_name.startswith('OneAgent') or entity_display_name.endswith(' System') or entity_display_name.startswith('Short-lived'):
                        continue

                management_zone_list = inner_entities_json.get('managementZones')
                for management_zone in management_zone_list:
                    management_zone_name = management_zone.get('name')
                    if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE':
                        rows.append((management_zone_name, 'DATABASE_SERVICE', entity_display_name))
                    else:
                        if management_zone_name == 'OPENSHIFT_ADMIN' and entity_type in openshift_admin_ignore_list:
                            continue
                        else:
                            rows.append((management_zone_name, entity_type, entity_display_name))

    rows = remove_duplicates(sorted(rows))

    report_writer.initialize_text_file(None)
    report_name = 'Management Zone Coverage Detail'
    report_headers = ['Management Zone', 'Entity Type', 'Entity Display Name']
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=(0, len(report_headers) - 1))
    report_writer.write_html(None, report_name, report_headers, rows)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
