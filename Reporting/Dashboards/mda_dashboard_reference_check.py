from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    mda_dict = {}

    # Note 'mdaId' is in the list solely to check for any MDA reference beyond the targets listed below it
    mda_list = [
        'mdaId',
        'dd458841-9bbe-4d3e-bb5e-5562e3420f8b',
        '144b80d2-dbf6-46e5-97d8-2d30355cde58',
        'c1b30b11-db5c-42f8-a67f-691496788ad9',
        '48ec22c7-3350-409f-aa2e-9500c3db81c9',

    ]
    for mda in mda_list:
        mda_dict[mda] = {'dashboards': []}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)
    dashboard_id_list = []
    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            dashboard_id_list.append(entity_id)
    for dashboard_id in sorted(dashboard_id_list):
        dashboard_json = dynatrace_api.get(env, token, endpoint + '/' + dashboard_id, params)
        for dashboard in dashboard_json:
            dashboard_metadata = dashboard.get('dashboardMetadata')
            name = dashboard_metadata.get('name')
            for mda in sorted(mda_list):
                if mda in str(dashboard):
                    try:
                        rows.append([f'MDA {mda} found in dashboard {name}'])
                        dashboard_list = mda_dict[mda].get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            mda_dict[mda]['dashboards'] = dashboard_list
                    except KeyError:
                        rows.append([f'MDA {mda} found in dashboard {name} but not in target list'])

    compile_findings(mda_dict, rows)

    report_name = 'MDA Dashboard References'
    report_writer.initialize_text_file(None)
    report_headers = ['Findings']
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def compile_findings(mda_dict, rows):
    keys = sorted(mda_dict.keys())
    for key in keys:
        mda_xref = mda_dict[key]
        mda_xref_keys = mda_xref.keys()
        for mda_xref_key in mda_xref_keys:
            if len(mda_xref[mda_xref_key]) > 0:
                rows.append([key + ' used in ' + mda_xref_key + ': ' + sort_and_stringify_list_items(mda_xref[mda_xref_key])])


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
