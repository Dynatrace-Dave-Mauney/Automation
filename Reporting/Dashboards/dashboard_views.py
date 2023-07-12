import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

xlsx_file_name = '../../$Output/Reporting/Dashboards/DashboardViews.xlsx'
html_file_name = '../../$Output/Reporting/Dashboards/DashboardViews.html'

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


def process():
    print(f'XLSX File: {xlsx_file_name}')
    print(f'HTML File: {html_file_name}')
    rows = []

    dashboard_details = load_dashboard_details()

    endpoint = '/api/v2/metrics/query'
    metric_schema_id = 'builtin:dashboards.viewCount'
    metric_query_options = ':splitBy("id"):avg:auto:sort(value(avg,descending)):fold:limit(100)'
    from_time = 'now-1M'
    params = 'metricSelector=' + urllib.parse.quote(metric_schema_id) + metric_query_options + '&from=' + from_time
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for metrics_json in metrics_json_list:
        result_list = metrics_json.get('result')
        for result in result_list:
            data = result.get('data')
            for datapoint in data:
                datapoint_value = datapoint.get('values')[0]
                dashboard_id = datapoint.get('dimensionMap').get('id').strip()
                dashboard_detail = dashboard_details.get(dashboard_id)
                if dashboard_detail:
                    dashboard_name = dashboard_detail.get('name', '')
                    dashboard_owner = dashboard_detail.get('owner', '')
                else:
                    # If user is not in "dynatrace.com", then they will get this for all "dynatrace.com" owners.
                    # So, we will double-check any missing ID by attempting to get it directly from the API
                    dashboard = get_dashboard(dashboard_id)
                    if dashboard:
                        dashboard_name = dashboard.get('dashboardMetadata').get('name', '')
                        dashboard_owner = dashboard.get('dashboardMetadata').get('owner', '')
                    else:
                        dashboard_name = '*** DELETED ***'
                        dashboard_owner = ''

                rows.append((dashboard_name, dashboard_id, dashboard_owner, datapoint_value))

    write_console(rows)
    write_xlsx(rows)
    write_html(rows)


def load_dashboard_details():
    dashboard_details = {}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')
            dashboard_details[entity_id] = {'name': name, 'owner': owner}

    return dashboard_details


def get_dashboard(dashboard_id):
    endpoint = f'/api/config/v1/dashboards/{dashboard_id}'
    params = ''
    dashboard_json_list = dynatrace_api.get(env, token, endpoint, params)
    if dashboard_json_list:
        dashboard = dashboard_json_list[0]
        if dashboard.get('dashboardMetadata'):
            return dashboard

    # Dashboard was not successfully retrieved
    return None


def write_console(rows):
    title = 'Dashboard Views'
    headers = ['Dashboard Name', 'Dashboard ID', 'Owner', 'Views']
    delimiter = '|'
    report_writer.write_console(title, headers, rows, delimiter)


def write_xlsx(rows):
    worksheet_name = 'Dashboard Views'
    headers = ['Dashboard Name', 'Dashboard ID', 'Owner', 'Views']
    header_format = None
    auto_filter = (2, 2)
    report_writer.write_xlsx(xlsx_file_name, worksheet_name, headers, rows, header_format, auto_filter)


def write_html(rows):
    page_heading = 'Dashboard Views'
    table_headers = ['Dashboard Name', 'Dashboard ID', 'Owner', 'Views']
    report_writer.write_html(html_file_name, page_heading, table_headers, rows)


if __name__ == '__main__':
    process()
