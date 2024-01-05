import base64
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

    count_total = 0
    count_has_dashboard_reference = 0
    count_has_no_dashboard_reference = 0

    slo_dict = {}

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:monitoring.slo'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=objectId,updateToken,value&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    slo_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for slo in slo_list:
        items = slo.get('items', [])
        if items:
            for item in items:
                value = item.get('value')
                name = value.get('name')
                update_token = item.get('updateToken')
                assigned_entity = object_id_to_entity_id(update_token)
                slo_dict[assigned_entity] = {'name': name, 'dashboards': []}

    endpoint = '/api/config/v1/dashboards'
    dashboards_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    dashboard_id_list = []
    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            owner = inner_dashboards_json.get('owner')
            if owner != 'Dynatrace':
                entity_id = inner_dashboards_json.get('id')
                dashboard_id_list.append(entity_id)

    for dashboard_id in sorted(dashboard_id_list):
        dashboard_json = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}/{dashboard_id}', token)
        for dashboard in dashboard_json:
            dashboard_metadata = dashboard.get('dashboardMetadata')
            name = dashboard_metadata.get('name')
            for slo_assigned_entity in sorted(slo_dict.keys()):
                if slo_assigned_entity in str(dashboard):
                    try:
                        dashboard_list = slo_dict[slo_assigned_entity].get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            slo_dict[slo_assigned_entity]['dashboards'] = dashboard_list
                    except KeyError:
                        rows.append([f'Obsolete SLO ID {slo_assigned_entity} referenced in dashboard {name}'])

    keys = sorted(slo_dict.keys())
    for key in keys:
        slo_xref = slo_dict[key]
        name = slo_xref['name']
        references = len(slo_xref['dashboards'])
        references_literal = 'dashboard'
        if references > 1:
            references_literal += 's'

        count_total += 1

        if references > 0:
            if not summary_mode:
                rows.append([f'The SLO named "{name}" with the assigned ID "{key}" is used in {references_literal} "{sort_and_stringify_list_items(slo_xref["dashboards"])}"'])
            count_has_dashboard_reference += 1
        else:
            if not summary_mode:
                rows.append([f'The SLO named "{name}" with the assigned ID "{key}" is not used in any dashboard'])
            count_has_no_dashboard_reference += 1

    summary.append(f'Of the {count_total} SLOs currently defined:')
    summary.append(f'{count_has_dashboard_reference} SLOs are referenced by one or more dashboards.')
    summary.append(f'{count_has_no_dashboard_reference} SLOs are not referenced by any dashboard.')

    if not summary_mode:
        report_name = 'SLO Dashboard References'
        report_writer.initialize_text_file(None)
        report_headers = ['Finding']
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)
        write_strings(summary)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


def object_id_to_entity_id(object_id):
    # Add double equals to force pad regardless of remainder
    # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding/49459036#49459036
    decoded_object_id_bytes = base64.urlsafe_b64decode(object_id + '==')

    # Remove the first 13 bytes and remove the bytes indicator while converting to a string
    schema_id = str(decoded_object_id_bytes[12:]).replace("b'", "")

    # Truncate after the first byte delimiter that indicates the end of the schema id
    entity_id = schema_id[:schema_id.find('\\')]

    # print(f'DEBUG object_id_to_entity_id parameters - entity_id: "{entity_id}" for object_id: {object_id} ')

    return entity_id


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, token)


if __name__ == '__main__':
    main()
