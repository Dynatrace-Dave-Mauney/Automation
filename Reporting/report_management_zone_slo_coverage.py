import copy
import re
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []

    management_zone_dict = load_management_zone_dict(env, token)
    # print(management_zone_dict)

    slos_found_settings_20 = count_slo_references(env, token, management_zone_dict)
    count_slo_references_from_env_v2_slo_api(env, token, management_zone_dict, slos_found_settings_20)
    # print(management_zone_dict)

    keys = management_zone_dict.keys()
    for key in sorted(keys):
        # print(key)
        slo_count_total = management_zone_dict[key]['Total']
        slo_count_browser = management_zone_dict[key]['Browser']
        slo_count_http = management_zone_dict[key]['HTTP']
        slo_count_service = management_zone_dict[key]['Service']
        slo_count_host = management_zone_dict[key]['Host']
        slo_count_mobile = management_zone_dict[key]['Mobile']
        slo_count_web = management_zone_dict[key]['Web']
        rows.append((key, slo_count_total, slo_count_browser, slo_count_http, slo_count_service, slo_count_host, slo_count_mobile, slo_count_web))

    rows = sorted(rows)
    report_name = 'MZ-SLO Cross-Reference'
    report_writer.initialize_text_file(None)
    report_headers = ('Management Zone', 'Total SLO References', 'Browser', 'HTTP', 'Service', 'Host', 'Mobile', 'Web')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def load_management_zone_dict(env, token):
    management_zone_dict_template = {'Total': 0, 'Browser': 0, 'HTTP': 0, 'Service': 0, 'Host': 0, 'Mobile': 0, 'Web': 0}

    management_zone_dict = {}

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)

    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        for inner_management_zones_json in inner_management_zones_json_list:
            name = inner_management_zones_json.get('name')
            # print(f'"{name}"')
            if name.endswith('-PROD') or name.endswith('-PRD') or name.endswith('-DR'):
                # management_zone_id = inner_management_zones_json.get('id')
                management_zone_dict[name] = copy.deepcopy(management_zone_dict_template)

    return management_zone_dict


def count_slo_references(env, token, management_zone_dict):
    count_standard_names_only = True
    slos_found_settings_20 = []

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:monitoring.slo'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_objects = dynatrace_api.get(env, token, endpoint, params)
    for settings_object in settings_objects:
        items = settings_object.get('items', [])

        if items:
            for item in items:
                value = item.get('value')
                # slo_summary = item.get('summary').replace('\\', '')
                name = value.get('name')
                slos_found_settings_20.append(name)
                metric_name = value.get('metricName')
                metric_expression = value.get('metricExpression')
                enabled = value.get('enabled')
                slo_filter = value.get('filter')

                if not enabled:
                    continue

                # if 'builtin:synthetic.http' in metric_expression or \
                #         'builtin:synthetic.browser' in metric_expression or \
                #         'builtin:service' in metric_expression or \
                #         'calc:service' in metric_expression or \
                #         'builtin:host' in metric_expression or \
                #         'builtin:apps.other' in metric_expression or \
                #         'builtin:apps.web' in metric_expression:
                #     pass
                # else:
                #     print(f'Unexpected metric expression reference by {name}: {metric_name}|{metric_expression}|{enabled}|{slo_filter}')

                # print(f'"{slo_filter}"')
                # print(f'{name}|{metric_name}|{metric_expression}|{enabled}|{slo_filter}')
                print(f'Settings 2.0 API Results: {name}|{slo_filter}')

                if 'mzName' in slo_filter:
                    management_zone_name = re.sub('.*mzName', '', slo_filter)
                    management_zone_name = re.sub(',.*', '', management_zone_name)
                    management_zone_name = management_zone_name.replace('(', '')
                    management_zone_name = management_zone_name.replace(')', '')
                    management_zone_name = management_zone_name.replace('"', '')
                    # print(f'{name}|{slo_filter}|{management_zone_name}')
                    try:
                        if count_standard_names_only:
                            browser_reference = f'{management_zone_name} - Synthetic Availability (Browser)'
                            http_reference = f'{management_zone_name} - Synthetic Availability (HTTP)'
                            service_reference = f'{management_zone_name} - Service'
                            host_reference = f'{management_zone_name} - Host Availability'
                            mobile_reference = 'NOT YET IMPLEMENTED!'
                            web_reference = 'NOT YET IMPLEMENTED!'

                            if browser_reference in name:
                                management_zone_dict[management_zone_name]['Browser'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if http_reference in name:
                                management_zone_dict[management_zone_name]['HTTP'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if service_reference in name:
                                management_zone_dict[management_zone_name]['Service'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if host_reference in name:
                                management_zone_dict[management_zone_name]['Host'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if mobile_reference in name:
                                management_zone_dict[management_zone_name]['Mobile'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if web_reference in name:
                                management_zone_dict[management_zone_name]['Web'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1
                        else:
                            browser_reference = 'builtin:synthetic.browser'
                            http_reference = 'builtin:synthetic.http'
                            service_reference = 'builtin:service'
                            host_reference = 'builtin:host'
                            mobile_reference = 'builtin:apps.other'
                            web_reference = 'builtin:apps.web'

                            if browser_reference in metric_expression:
                                management_zone_dict[management_zone_name]['Browser'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if http_reference in metric_expression:
                                management_zone_dict[management_zone_name]['HTTP'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if service_reference in metric_expression or 'calc:service' in metric_expression:
                                management_zone_dict[management_zone_name]['Service'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if host_reference in metric_expression:
                                management_zone_dict[management_zone_name]['Host'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if mobile_reference in metric_expression:
                                management_zone_dict[management_zone_name]['Mobile'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                            if web_reference in metric_expression:
                                management_zone_dict[management_zone_name]['Web'] += 1
                                management_zone_dict[management_zone_name]['Total'] += 1

                        # print(f'Management zone "{management_zone_name}" referenced by SLO "{name}"')
                    except KeyError:
                        print(f'Management zone "{management_zone_name}" referenced by SLO "{name}" no longer exists!')

    return slos_found_settings_20


def count_slo_references_from_env_v2_slo_api(env, token, management_zone_dict, slos_found_settings_20):
    endpoint = '/api/v2/slo'
    raw_params = f'&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    slo_objects = dynatrace_api.get(env, token, endpoint, params)
    for slo_object in slo_objects:
        items = slo_object.get('slo', [])

        if items:
            for item in items:
                # value = item.get('value')
                # slo_summary = item.get('summary').replace('\\', '')
                name = item.get('name')

                if name in slos_found_settings_20:
                    continue

                metric_name = item.get('metricKey')
                metric_expression = item.get('metricExpression')
                enabled = item.get('enabled')
                slo_filter = item.get('filter')

                if not enabled:
                    continue

                if 'builtin:synthetic.http' in metric_expression or \
                        'builtin:synthetic.browser' in metric_expression or \
                        'builtin:service' in metric_expression or \
                        'calc:service' in metric_expression or \
                        'builtin:host' in metric_expression or \
                        'builtin:apps.other' in metric_expression or \
                        'builtin:apps.web' in metric_expression:
                    pass
                else:
                    print(f'Unexpected metric expression reference by {name}: {metric_name}|{metric_expression}|{enabled}|{slo_filter}')

                # print(f'"{slo_filter}"')
                # print(f'{name}|{metric_name}|{metric_expression}|{enabled}|{slo_filter}')
                print(f'Environment V2 SLO API Results: {name}|{slo_filter}')

                if 'mzName' in slo_filter:
                    management_zone_name = re.sub('.*mzName', '', slo_filter)
                    management_zone_name = re.sub(',.*', '', management_zone_name)
                    management_zone_name = management_zone_name.replace('(', '')
                    management_zone_name = management_zone_name.replace(')', '')
                    management_zone_name = management_zone_name.replace('"', '')
                    # print(f'{name}|{slo_filter}|{management_zone_name}')
                    try:
                        management_zone_dict[management_zone_name]['Total'] += 1

                        if 'builtin:synthetic.browser' in metric_expression:
                            management_zone_dict[management_zone_name]['Browser'] += 1

                        if 'builtin:synthetic.http' in metric_expression:
                            management_zone_dict[management_zone_name]['HTTP'] += 1

                        if 'builtin:service' in metric_expression or 'calc:service' in metric_expression:
                            management_zone_dict[management_zone_name]['Service'] += 1

                        if 'builtin:host' in metric_expression:
                            management_zone_dict[management_zone_name]['Host'] += 1

                        if 'builtin:apps.other' in metric_expression:
                            management_zone_dict[management_zone_name]['Mobile'] += 1

                        if 'builtin:apps.web' in metric_expression:
                            management_zone_dict[management_zone_name]['Web'] += 1

                        # print(f'Management zone "{management_zone_name}" referenced by SLO "{name}"')
                    except KeyError:
                        print(f'Management zone "{management_zone_name}" referenced by SLO "{name}" no longer exists!')


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
