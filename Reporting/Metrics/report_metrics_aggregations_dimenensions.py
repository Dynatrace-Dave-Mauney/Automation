import sys
import urllib

from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    endpoint = '/api/v2/metrics'
    raw_params = 'pageSize=500&fields=displayName,description,aggregationTypes,dimensionDefinitions'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    metrics_json_list = dynatrace_api.get(env, token, endpoint, params)
    print('metricId|displayName or description|aggregationTypes|dimensionDefinitions')
    for metrics_json in metrics_json_list:
        inner_metrics_json_list = metrics_json.get('metrics')
        for inner_metrics_json in inner_metrics_json_list:
            metric_id = inner_metrics_json.get('metricId')
            display_name = inner_metrics_json.get('displayName')
            description = inner_metrics_json.get('description')
            name_or_desc = format_name_or_desc(display_name, description)
            aggregation_types = format_aggs(inner_metrics_json.get('aggregationTypes'))
            dimension_definitions = format_dims(inner_metrics_json.get('dimensionDefinitions'))
            print(f'{metric_id}|{name_or_desc}|{str(aggregation_types)}|{str(dimension_definitions)}')
    print('Done!')

def format_name_or_desc(displayName, description):
    if displayName and displayName > '':
        return displayName
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


def run():
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


def main(arguments):
    usage = '''
    metrics_report.py: Report Metrics 

    Usage:    metrics_report.py <tenant/environment URL> <token>
    Examples: metrics_report.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              metrics_report.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
    '''

    # print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
    if len(arguments) < 2:
        print(usage)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments[1], arguments[2])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)

'''
Example Metric JSON:
{
  "metricId": "builtin:host.cpu.usage",
  "displayName": "CPU usage %",
  "description": "Percentage of CPU time currently utilized.",
  "unit": "Percent",
  "dduBillable": false,
  "created": 0,
  "lastWritten": 1676482142044,
  "entityType": [
    "HOST"
  ],
  "aggregationTypes": [
    "auto",
    "avg",
    "max",
    "min"
  ],
  "transformations": [
    "filter",
    "fold",
    "limit",
    "merge",
    "names",
    "parents",
    "timeshift",
    "sort",
    "last",
    "splitBy",
    "lastReal",
    "setUnit"
  ],
  "defaultAggregation": {
    "type": "avg"
  },
  "dimensionDefinitions": [
    {
      "key": "dt.entity.host",
      "name": "Host",
      "displayName": "Host",
      "index": 0,
      "type": "ENTITY"
    }
  ],
  "tags": [],
  "metricValueType": {
    "type": "unknown"
  },
  "scalar": false,
  "resolutionInfSupported": true
}
'''
