import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(SERVICE)&fields=+properties,+fromRelationships&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            properties = inner_entities_json.get('properties')
            service_type = properties.get('serviceType', 'NONE')

            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            if 'Requests' not in display_name:
                continue

            if 'public networks' not in display_name:
                continue

            r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
            external = r.json()

            to_relationships = external.get('toRelationships')
            is_group_of = to_relationships.get('isGroupOf')
            for group in is_group_of:
                group_type = group.get('type')
                if group_type == 'SERVICE_METHOD_GROUP':
                    service_method_id = group.get('id')
                    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{service_method_id}', token)
                    external_service_method = r.json()
                    domain = external_service_method.get('displayName')

                    if not summary_mode:
                        rows.append([domain])

            if rows:
                rows = sorted(rows)
                summary.append('The following domains are called from "Requests to public networks" service:')
                for row in rows:
                    summary.append(row[0])

    if not summary_mode:
        report_name = 'External Domains Called'
        report_writer.initialize_text_file(None)
        report_headers = (['Domain'])
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
