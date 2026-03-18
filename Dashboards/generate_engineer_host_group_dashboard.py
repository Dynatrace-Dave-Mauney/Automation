import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

engineer_dashboard_prefix = '00000001-0000-0000-0001-'
engineer_dashboard_name = 'Engineer: Host Group'
engineer_dashboard_id = f'{engineer_dashboard_prefix}000000000002'


def process_host_group_tags(env, token):
    host_group_list = []

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST)&from=-5m&fields=properties,tags,managementZones'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # display_name = inner_entities_json.get('displayName', '')
            # properties = inner_entities_json.get('properties')

            tags = inner_entities_json.get('tags', [])

            tier_value = 'None'
            tier_value = 'None'

            for tag in tags:
                key = tag.get('key')
                if key == 'Host Group':
                    host_group_value = tag.get('value')
                    # print(host_group_value)
                if key == 'primary_tags.tier':
                    tier_value = tag.get('value', 'None')
                    # print(tier_value)

            if tier_value == '1':
                if host_group_value not in host_group_list:
                    host_group_list.append(host_group_value)

    # for host_group in sorted(host_group_list):
    #     print(host_group)

    management_zones = get_management_zones(env, token)

    put_engineer_dashboard(env, token, sorted(host_group_list), management_zones)


def put_engineer_dashboard(env, token, host_group_list, management_zones):
    engineer_dashboard = load_engineer_dashboard_template()

    engineer_dashboard['id'] = engineer_dashboard_id
    engineer_dashboard['dashboardMetadata']['name'] = engineer_dashboard_name
    engineer_dashboard['dashboardMetadata']['shared'] = True
    engineer_dashboard['dashboardMetadata']['preset'] = True

    all_host_groups = engineer_dashboard['tiles'][0:5]
    tier1_host_groups = engineer_dashboard['tiles'][5:10]
    tier0_host_groups = engineer_dashboard['tiles'][10:15]
    host_group_template = engineer_dashboard['tiles'][15:20]

    new_tiles = []
    new_tiles.extend(all_host_groups)
    new_tiles.extend(tier1_host_groups)
    new_tiles.extend(tier0_host_groups)

    top = host_group_template[0]['bounds']['top']
    left = host_group_template[0]['bounds']['left']
    height = host_group_template[0]['bounds']['height']

    for host_group in host_group_list:
        mz_name = f'HG: {host_group}'
        mz_id = management_zones[mz_name]
        # print(host_group, mz_name, mz_id)
        host_group_tiles = build_host_group_tiles(top, left, host_group, mz_name, mz_id, host_group_template)
        new_tiles.extend(host_group_tiles)
        top += height

        # Near actual max of 4864
        # if top >= 4712:
        # Nice stopping point for even splitting
        if top >= 4104:
            top = 0
            left += 1178

    engineer_dashboard['tiles'] = new_tiles

    endpoint = '/api/config/v1/dashboards'
    formatted_engineer_dashboard = json.dumps(engineer_dashboard, indent=4, sort_keys=False)
    dynatrace_api.put(env, token, endpoint, engineer_dashboard_id, formatted_engineer_dashboard)
    print(f'PUT {engineer_dashboard_name} dashboard to {env}/#dashboard;id={engineer_dashboard_id}')
    print('')


def build_host_group_tiles(top, left, host_group, mz_name, mz_id, host_group_template):
    # print(top, left)
    new_tiles = []
    template = copy.deepcopy(host_group_template)
    for tile in template:
        name = tile.get('name')
        if name == 'Markdown':
            tile['markdown'] = f'# {host_group}'
        else:
            tile['tileFilter']['managementZone']['id'] = mz_id
            tile['tileFilter']['managementZone']['name'] = mz_name
        tile['bounds']['top'] = top
        tile['bounds']['left'] = tile['bounds']['left'] + left
        new_tiles.append(tile)
        # print(tile)

    return new_tiles

def load_engineer_dashboard_template():
    with open('engineer_dashboard_template.json', 'r', encoding='utf-8') as infile:
        string = infile.read()
        return json.loads(string)


def get_management_zones(env, token):
    management_zones = {}
    endpoint = '/api/config/v1/managementZones'
    management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)
    mz_list = management_zones_json_list[0].get('values')
    for mz in mz_list:
        mz_name = mz.get('name')
        mz_id = mz.get('id')
        management_zones[mz_name] = mz_id

    return management_zones


def process(env, token):
    return process_host_group_tags(env, token)


def main():
    env_name, env, token = environment.get_environment('Prod')

    process(env, token)


if __name__ == '__main__':
    main()
