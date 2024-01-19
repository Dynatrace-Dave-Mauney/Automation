import urllib.parse

from requests.exceptions import HTTPError
from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []

    dashboard_details = load_dashboard_details(env, token)

    endpoint = '/api/v2/metrics/query'
    metric_schema_id = 'builtin:dashboards.viewCount'
    metric_query_options = ':splitBy("id"):avg:auto:sort(value(avg,descending)):fold:limit(100)'
    from_time = 'now-1M'
    params = 'metricSelector=' + urllib.parse.quote(metric_schema_id) + metric_query_options + '&from=' + from_time
    metrics_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
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
                    dashboard = get_dashboard(env, token, dashboard_id)
                    if dashboard:
                        dashboard_name = dashboard.get('dashboardMetadata').get('name', '')
                        dashboard_owner = dashboard.get('dashboardMetadata').get('owner', '')
                    else:
                        dashboard_name = '*** DELETED ***'
                        dashboard_owner = ''

                rows.append((dashboard_name, dashboard_id, dashboard_owner, datapoint_value))

    report_name = 'Dashboard Views'
    report_headers = ['Dashboard Name', 'Dashboard ID', 'Owner', 'Views']
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=(2, 2))
    report_writer.write_html(None, report_name, report_headers, rows)


def load_dashboard_details(env, token):
    dashboard_details = {}

    endpoint = '/api/config/v1/dashboards'
    dashboards_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')
            dashboard_details[entity_id] = {'name': name, 'owner': owner}

    return dashboard_details


def get_dashboard(env, token, dashboard_id):
    dashboard = None
    endpoint = f'/api/config/v1/dashboards/{dashboard_id}'
    try:
        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token, handle_exceptions=False)
        dashboard = r.json()
    except HTTPError as e:
        if not '404' in str(e):
            print('Oopsie!')

    if dashboard and dashboard.get('dashboardMetadata'):
        return dashboard

    # Dashboard was not successfully retrieved
    return None


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
