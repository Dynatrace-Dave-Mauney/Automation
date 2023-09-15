import urllib

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process(env, token):
    rows = []
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=500&fields=displayName,description,aggregationTypes,dimensionDefinitions'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')

            # To report specific metric types
            # if 'calc:service' not in metric_id:
            #    continue

            display_name = inner_metrics_json.get('displayName')
            description = inner_metrics_json.get('description')
            name_or_desc = format_name_or_desc(display_name, description)
            aggregation_types = format_aggs(inner_metrics_json.get('aggregationTypes'))
            dimension_definitions = format_dims(inner_metrics_json.get('dimensionDefinitions'))
            rows.append((metric_id, name_or_desc, str(aggregation_types), str(dimension_definitions)))

    report_name = 'Metric Aggregations+Dimensions'
    report_writer.initialize_text_file(None)
    report_headers = ('Metric ID', 'Name or Description', 'Aggregation Types', 'Dimension Definitions')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def format_name_or_desc(display_name, description):
    if display_name and display_name > '':
        return display_name
    else:
        return description


def format_aggs(aggs):
    formatted_agg_list = []
    for agg in aggs:
        if agg != 'auto':
            formatted_agg_list.append(agg)
    return str(formatted_agg_list).replace("'", '').replace('[', '').replace(']', '')


def format_dims(dims):
    formatted_dim_list = []
    for dim in dims:
        formatted_dim_list.append(dim.get('key'))
    dims_string = str(formatted_dim_list).replace("'", '').replace('[', '').replace(']', '')
    if dims_string > '':
        return dims_string
    else:
        return 'None'


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
