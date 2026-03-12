import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

executive_dashboard_prefix = '00000001-0000-0000-0001-'
executive_dashboard_name = 'Executive'
executive_dashboard_id = f'{executive_dashboard_prefix}000000000001'

# top = 0
# left = 0
height = 152
width = 570
# 570 works fine, 190 does not work!
# width = 380

def process_app_tags(env, token):
    app_list = []

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

            for tag in tags:
                key = tag.get('key')
                if key == 'primary_tags.app':
                    app_value = tag.get('value')
                if key == 'primary_tags.tier':
                    tier_value = tag.get('value')

            if tier_value == '1':
                if app_value not in app_list:
                    app_list.append(app_value)

    # for app in sorted(app_list):
    #     print(app)

    management_zones = get_management_zones(env, token)

    put_executive_dashboard(env, token, sorted(app_list), management_zones)


def put_executive_dashboard(env, token, app_list, management_zones):
    executive_dashboard = load_executive_dashboard_template()

    executive_dashboard['id'] = executive_dashboard_id
    executive_dashboard['dashboardMetadata']['name'] = executive_dashboard_name
    executive_dashboard['dashboardMetadata']['shared'] = True
    executive_dashboard['dashboardMetadata']['preset'] = True

    all_apps = executive_dashboard['tiles'][0:1]
    tier1_apps = executive_dashboard['tiles'][1:2]
    tier0_apps = executive_dashboard['tiles'][2:3]
    app_template = executive_dashboard['tiles'][3:4]

    # print('app_apps:', all_apps)
    # print('tier1_apps:', tier1_apps)
    # print('tier0_apps:', tier0_apps)
    # print('app_template:', app_template)

    new_tiles = []
    new_tiles.extend(all_apps)
    new_tiles.extend(tier1_apps)
    new_tiles.extend(tier0_apps)

    # global top
    # global left
    global width
    top = app_template[0]['bounds']['top']
    left = app_template[0]['bounds']['left']
    # height = app_template[0]['bounds']['height']
    # width = app_template[0]['bounds']['width']
    print(top, left, height, width)

    for app in app_list:
        mz_name = f'APP:{app}'
        mz_id = management_zones[mz_name]
        # print(app, mz_name, mz_id)
        app_tiles = build_app_tiles(top, left, app, mz_name, mz_id, app_template)
        new_tiles.extend(app_tiles)
        top += height

        # Near actual max of 4864
        # if top >= 4712:
        # Nice stopping point for even splitting
        if top >= 2736:
            top = 0
            left += width

    executive_dashboard['tiles'] = new_tiles

    endpoint = '/api/config/v1/dashboards'
    formatted_executive_dashboard = json.dumps(executive_dashboard, indent=4, sort_keys=False)
    dynatrace_api.put(env, token, endpoint, executive_dashboard_id, formatted_executive_dashboard)
    print(f'PUT {executive_dashboard_name} dashboard to {env}/#dashboard;id={executive_dashboard_id}')
    print('')


def build_app_tiles(top, left, app, mz_name, mz_id, app_template):
    # print(top, left)
    new_tiles = []
    template = copy.deepcopy(app_template)
    for tile in template:
        name = tile.get('name')
        # print(name)
        if name != 'All Problems' and name != 'Tier 1 Problems' and name != 'Non Tier 1 Problems':
            tile['name'] = app
        if tile.get('tileFilter', {}).get('managementZone', {}).get('id', {}):
            tile['tileFilter']['managementZone']['id'] = mz_id
            tile['tileFilter']['managementZone']['name'] = mz_name
        tile['bounds']['top'] = top
        tile['bounds']['left'] = tile['bounds']['left'] + left
        tile['bounds']['height'] = height
        tile['bounds']['width'] = width
        new_tiles.append(tile)
        # print(tile)

    return new_tiles

def load_executive_dashboard_template():
    with open('executive_dashboard_template.json', 'r', encoding='utf-8') as infile:
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
    return process_app_tags(env, token)


def main():
    env_name, env, token = environment.get_environment('Prod')

    process(env, token)


if __name__ == '__main__':
    main()
