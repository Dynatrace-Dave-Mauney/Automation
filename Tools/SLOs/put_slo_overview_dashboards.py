import base64
import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

slo_overview_dashboard_prefix = '00000001-0000-0000-0001-'
slo_overview_menu_dashboard_name = 'SLO Overview Menu'
slo_overview_menu_dashboard_id = f'{slo_overview_dashboard_prefix}000000000000'

# Fake Examples
slo_skip_list = [
    'FAKE1-PROD',
    'FAKE2-PROD',
]

def process_slos(env, token):
    slo_list = []

    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:monitoring.slo'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=objectId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object = dynatrace_api.get(env, token, endpoint, params)[0]
    items = settings_object.get('items', [])

    if items:
        for item in items:
            object_id = item.get('objectId')
            value = item.get('value')
            # slo_summary = item.get('summary')
            name = value.get('name')
            metric_name = value.get('metricName')
            # metric_expression = value.get('metricExpression')
            enabled = value.get('enabled')
            if enabled and name not in slo_skip_list:
                slo_list.append((name, metric_name, object_id))

    put_slo_overview_dashboards(env, token, sorted(slo_list))


def put_slo_overview_dashboards(env, token, slo_list):
    dashboard_coverage = []

    dashboard_number = 1

    new_tiles = []

    slo_overview_dashboard = load_slo_overview_dashboard_template()

    slo_overview_dashboard['dashboardMetadata']['shared'] = True
    slo_overview_dashboard['dashboardMetadata']['preset'] = True

    tiles = slo_overview_dashboard['tiles']
    slo_tile = tiles[0]
    slo_metric_tile = tiles[1]
    slo_error_budget_tile = tiles[2]
    slo_budget_burn_rate_tile = tiles[3]

    # print(slo_tile)
    # print(slo_metric_tile)
    # print(slo_error_budget_tile)
    # print(slo_budget_burn_rate_tile)

    top = 0

    for slo in slo_list:
        name, metric_name, object_id = slo
        # print(name, metric_name, object_id)

        if top == 0:
            first_slo_name = name

        slo_tile['assignedEntities'] = [get_assigned_entity(env, token, object_id)]
        slo_tile['metric'] = f'METRICS=true;LEGEND=true;PROBLEMS=true;decimals=10;customTitle={name};'
        slo_tile['bounds']['top'] = top
        # print(slo_tile)

        slo_metric_tile['queries'][0]['metric'] = f'func:slo.{metric_name}'
        slo_metric_tile['metricExpressions'] = [f'resolution=null&(func:slo.{metric_name}:splitBy():sort(value(auto,descending)):limit(20)):limit(100):names']
        slo_metric_tile['bounds']['top'] = top
        # print(slo_metric_tile)

        slo_error_budget_tile['queries'][0]['metric'] = f'func:slo.errorBudget.{metric_name}'
        slo_error_budget_tile['metricExpressions'] = [f'resolution=null&(func:slo.errorBudget.{metric_name}:splitBy():sort(value(auto,descending)):limit(20)):limit(100):names']
        slo_error_budget_tile['bounds']['top'] = top
        # print(slo_error_budget_tile)

        slo_budget_burn_rate_tile['queries'][0]['metric'] = f'func:slo.errorBudgetBurnRate.{metric_name}'
        slo_budget_burn_rate_tile['metricExpressions'] = [f'resolution=null&(func:slo.errorBudgetBurnRate.{metric_name}:splitBy():sort(value(auto,descending)):limit(20)):limit(100):names']
        slo_budget_burn_rate_tile['bounds']['top'] = top
        # print(slo_budget_burn_rate_tile)

        new_tiles.append(copy.deepcopy(slo_tile))
        new_tiles.append(copy.deepcopy(slo_metric_tile))
        new_tiles.append(copy.deepcopy(slo_error_budget_tile))
        new_tiles.append(copy.deepcopy(slo_budget_burn_rate_tile))

        top += 228

        if top > 4560:
            last_slo_name = name
            put_dashboard(env, token, dashboard_number, slo_overview_dashboard, new_tiles)
            top = 0
            new_tiles = []
            dashboard_coverage.append((first_slo_name, last_slo_name))
            dashboard_number += 1

    if top > 0:
        last_slo_name = name
        dashboard_coverage.append((first_slo_name, last_slo_name))
        put_dashboard(env, token, dashboard_number, slo_overview_dashboard, new_tiles)

    put_slo_overview_menu_dashboard(env, token, dashboard_coverage)


def put_slo_overview_menu_dashboard(env, token, dashboard_coverage):
    slo_overview_menu_dashboard = load_slo_overview_menu_dashboard_template()

    slo_overview_menu_dashboard['id'] = slo_overview_menu_dashboard_id
    slo_overview_menu_dashboard['dashboardMetadata']['name'] = slo_overview_menu_dashboard_name
    slo_overview_menu_dashboard['dashboardMetadata']['shared'] = True
    slo_overview_menu_dashboard['dashboardMetadata']['preset'] = True

    # print(dashboard_coverage)

    markdown = ''
    index = 1
    for slo_range in dashboard_coverage:
        first, last = slo_range
        markdown += f'[{first} to {last}](#dashboard;id={slo_overview_dashboard_prefix}{index:012})  \n'
        index += 1
    print(markdown)
    slo_overview_menu_dashboard['tiles'][0]['markdown'] = markdown

    endpoint = '/api/config/v1/dashboards'
    formatted_slo_overview_menu_dashboard = json.dumps(slo_overview_menu_dashboard, indent=4, sort_keys=False)
    dynatrace_api.put(env, token, endpoint, slo_overview_menu_dashboard_id, formatted_slo_overview_menu_dashboard)
    print(f'PUT {slo_overview_menu_dashboard_name} dashboard to {env}) with id: {slo_overview_menu_dashboard_id}')
    print('')


def load_slo_overview_menu_dashboard_template():
    with open('slo_overview_menu_dashboard_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def put_dashboard(env, token, dashboard_number, slo_overview_dashboard, new_tiles):
    dashboard_name = f'SLO Overview - {dashboard_number}'
    dashboard_id = slo_overview_dashboard_prefix + f'{dashboard_number:012}'

    slo_overview_dashboard['id'] = dashboard_id
    slo_overview_dashboard['dashboardMetadata']['name'] = dashboard_name

    slo_overview_dashboard['tiles'] = new_tiles

    endpoint = '/api/config/v1/dashboards'
    formatted_slo = json.dumps(slo_overview_dashboard, indent=4, sort_keys=False)
    dynatrace_api.put(env, token, endpoint, dashboard_id, formatted_slo)
    print(f'PUT {dashboard_name} dashboard to {env}) with id: {dashboard_id}')
    print('')


def get_assigned_entity(env, token, object_id):
    endpoint = '/api/v2/settings/objects'
    settings_object = dynatrace_api.get_by_object_id(env, token, endpoint, object_id)
    update_token = settings_object.get('updateToken')
    assigned_entity = object_id_to_entity_id(update_token)
    return assigned_entity


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


def load_slo_overview_dashboard_template():
    with open('slo_overview_dashboard_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def process(env, token):
    return process_slos(env, token)


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def main():
    env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    # env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token)


if __name__ == '__main__':
    main()
