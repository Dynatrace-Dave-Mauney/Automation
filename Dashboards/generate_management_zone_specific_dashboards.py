# NOTE: Be sure to PUT the standard "Overview" dashboard in the tenant
#       before running this process, which uses that dashboard as a template

import copy
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

entity_types_of_interest = [
    # DATABASE_SERVICE and EXTERNAL_SERVICE are "pseudo-services"
    # TODO: KUBERNETES could be added later because it is just "side menu" stuff.  MOBILE_APPLICATION is not needed yet since no MZ is used for the one that exists.
    'APPLICATION',
    'BROWSER',
    'HTTP_CHECK',
    'SERVICE',
    'EXTERNAL_SERVICE',
    'DATABASE_SERVICE',
    'PROCESS_GROUP',
    'HOST',
    # 'KUBERNETES_CLUSTER',
    # 'KUBERNETES_NODE',
    # 'KUBERNETES_SERVICE',
]

overview_markdown = '#### [\u21e6 Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\n![BackButton]()'


def process(env, token):
    if 'DATABASE_SERVICE' in entity_types_of_interest and 'SERVICE' not in entity_types_of_interest:
        print('The "entity_types_of_interest" list must include "SERVICE" if "DATABASE_SERVICE" is included.')
        exit(1)

    if 'EXTERNAL_SERVICE' in entity_types_of_interest and 'SERVICE' not in entity_types_of_interest:
        print('The "entity_types_of_interest" list must include "SERVICE" if "EXTERNAL_SERVICE" is included.')
        exit(1)

    mz_coverage_dict = {}
    mz_id_lookup_dict = {}
    menu_dashboard_dict = {}

    counts_by_entity_type_template = {}
    for entity_type_of_interest in entity_types_of_interest:
        counts_by_entity_type_template[entity_type_of_interest] = 0

    endpoint = '/api/config/v1/managementZones'
    management_zone_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            mz_name = inner_management_zone_json.get('name')
            mz_id = inner_management_zone_json.get('id')
            mz_coverage_dict[mz_name] = copy.deepcopy(counts_by_entity_type_template)
            mz_id_lookup_dict[mz_name] = mz_id

    for entity_type_of_interest in entity_types_of_interest:
        get_mz_coverage_for_entity_type(env, token, entity_type_of_interest, mz_coverage_dict)

    endpoint = '/api/config/v1/dashboards'

    dashboard_template = get_dashboard_template(env, token)
    # print('Building Dashboard Tile Template Dictionary')
    dashboard_tile_template_dict = {}
    dashboard_tiles = dashboard_template.get('tiles')

    # TODO: Remove debug code!
    # sorted_dashboard_tiles = sort_dashboard_tiles(dashboard_tiles)
    # print('Sorted Dashboard Template Tiles:')
    # for tile in sorted_dashboard_tiles:
    #     print('name/top/left:', tile['name'], tile['bounds']['top'], tile['bounds']['left'])
    # exit(1111)

    for dashboard_tile in dashboard_tiles:
        # print('dashboard_tile:', dashboard_tile)
        dashboard_tile_name = dashboard_tile.get('name')
        dashboard_tile_template_dict[dashboard_tile_name] = dashboard_tile

    # print('Dashboard Tile Template:', dashboard_tile_template_dict)

    for key in sorted(mz_coverage_dict.keys()):
        entity_type_list = get_entity_type_list(key, mz_coverage_dict)
        mz_id = mz_id_lookup_dict.get(key).zfill(19)
        mz_dashboard_id = convert_mz_id_to_db_id(mz_id)
        # print('Input:', key, mz_id, mz_dashboard_id, entity_type_list)

        dashboard = copy.deepcopy(dashboard_template)
        dashboard['id'] = mz_dashboard_id
        dashboard_template_name = dashboard.get('dashboardMetadata').get('name')
        dashboard_name = f'{dashboard_template_name} for {key}'
        dashboard['dashboardMetadata']['name'] = dashboard_name
        dashboard['dashboardMetadata']['dashboardFilter'] = {"managementZone": {"id": mz_id, "name": key}}

        variable_column_left = 0
        variable_column_width = 228
        variable_row_top = 266
        variable_row_height = 266

        new_tiles = []
        for entity_type in entity_type_list:
            # print(entity_type)
            if entity_type == 'APPLICATION':
                new_tile = dashboard_tile_template_dict.get('Applications Markdown')
                new_tile['bounds']['left'] = variable_column_left
                new_tile['markdown'] = '[Web Apps](#dashboard;id=00000000-dddd-bbbb-ffff-000000000002)'
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Application health')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                variable_column_left += variable_column_width
            if entity_type == 'BROWSER' or entity_type == 'HTTP_CHECK':
                new_tile = dashboard_tile_template_dict.get('Synthetics Markdown')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Synthetic monitor health')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                variable_column_left += variable_column_width
            if entity_type == 'SERVICE':
                new_tile = dashboard_tile_template_dict.get('Services Markdown')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Service health')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Service Response Time')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Service Failure Rate')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Service Request Count')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                variable_column_left += variable_column_width
                variable_row_top += variable_row_height
            if entity_type == 'EXTERNAL_SERVICE':
                new_tile = dashboard_tile_template_dict.get('Third Party Services Markdown')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Third Party Service health')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                variable_column_left += variable_column_width
                # new_tile = dashboard_tile_template_dict.get('Third Party Service Response Time')
                # new_tile['bounds']['top'] = variable_row_top
                # new_tiles.append(new_tile)
                # new_tile = dashboard_tile_template_dict.get('Third Party Service Failure Rate')
                # new_tile['bounds']['top'] = variable_row_top
                # new_tiles.append(new_tile)
                # new_tile = dashboard_tile_template_dict.get('Third Party Service Request Count')
                # new_tile['bounds']['top'] = variable_row_top
                # new_tiles.append(new_tile)
                # variable_row_top += variable_row_height
                new_tile = dashboard_tile_template_dict.get('Third Party Service Response Time Graph')
                new_tile['bounds']['top'] = variable_row_top
                new_tile['name'] = new_tile['name'].replace(' Graph', '')
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Third Party Service Failure Rate Graph')
                new_tile['bounds']['top'] = variable_row_top
                new_tile['name'] = new_tile['name'].replace(' Graph', '')
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Third Party Service Request Count Graph')
                new_tile['bounds']['top'] = variable_row_top
                new_tile['name'] = new_tile['name'].replace(' Graph', '')
                new_tiles.append(new_tile)
                variable_row_top += variable_row_height
            if entity_type == 'DATABASE_SERVICE':
                new_tile = dashboard_tile_template_dict.get('Databases Markdown')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Database health')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                variable_column_left += variable_column_width
            if entity_type == 'PROCESS_GROUP':
                new_tile = dashboard_tile_template_dict.get('Process CPU')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Process Memory')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                variable_row_top += variable_row_height
            if entity_type == 'HOST':
                new_tile = dashboard_tile_template_dict.get('Hosts Markdown')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Host health')
                new_tile['bounds']['left'] = variable_column_left
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Host CPU')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                new_tile = dashboard_tile_template_dict.get('Host Memory')
                new_tile['bounds']['top'] = variable_row_top
                new_tiles.append(new_tile)
                variable_column_left += variable_column_width
                variable_row_top += variable_row_height

        new_tile = dashboard_tile_template_dict.get('Problems Markdown')
        new_tile['bounds']['left'] = variable_column_left
        new_tile['markdown'] = overview_markdown
        new_tiles.append(new_tile)
        new_tile = dashboard_tile_template_dict.get('Problems')
        new_tile['bounds']['left'] = variable_column_left
        new_tiles.append(new_tile)
        variable_column_left += variable_column_width

        new_tile = dashboard_tile_template_dict.get('Management Zone Overview Links Markdown')
        new_tile['bounds']['top'] = variable_row_top
        new_tiles.append(new_tile)
        new_tile = dashboard_tile_template_dict.get('More Details Markdown')
        new_tile['bounds']['top'] = variable_row_top
        new_tiles.append(new_tile)

        # for new_tile in new_tiles:
        #     print(new_tile)

        dashboard['tiles'] = new_tiles

        print(dashboard_name, f'{env}/#dashboard;id={mz_dashboard_id}')
        dynatrace_api.put_object(f'{env}{endpoint}/{mz_dashboard_id}', token, json.dumps(dashboard))
        menu_dashboard_dict[dashboard_name] = [mz_dashboard_id, mz_id_lookup_dict[key]]

    menu_dashboard = generate_menu_dashboard(dashboard_template, menu_dashboard_dict)
    menu_dashboard_name = menu_dashboard['dashboardMetadata']['name']
    menu_dashboard_id = menu_dashboard['id']
    print(f'{menu_dashboard_name}: {env}/#dashboard;id={menu_dashboard_id}')
    dynatrace_api.put_object(f'{env}{endpoint}/{menu_dashboard_id}', token, json.dumps(menu_dashboard))


def generate_menu_dashboard(dashboard_template, menu_dashboard_dict):
    dashboard = copy.deepcopy(dashboard_template)
    dashboard['id'] = '00000000-dddd-0000-0000-000000000001'
    dashboard['dashboardMetadata']['name'] = 'Management Zone Overview Links'

    markdown_menu = dict()
    markdown_menu['name'] = ''
    markdown_menu['tileType'] = 'MARKDOWN'
    markdown_menu['configured'] = True
    markdown_menu['bounds'] = {"top": 0, "left": 0, "width": 380, "height": 1102}
    markdown_menu['tileFilter'] = {}
    markdown_menu['isAutoRefreshDisabled'] = False

    markdown_menu_code = ''
    for key in menu_dashboard_dict.keys():
        markdown_menu_code += f'[{key.replace("Prod: Overview for ", "")}](#dashboard;id={menu_dashboard_dict[key][0]};gf={menu_dashboard_dict[key][1]})  \n'

    markdown_menu['markdown'] = markdown_menu_code
    dashboard['tiles'] = [markdown_menu]

    return dashboard


def sort_dashboard_tiles(tiles):
    # print('sort_dashboard_tiles(tiles): tiles:', tiles)
    # for tile in tiles:
    #     print(tile)
    #     print(tile['bounds'])
    sorted_tiles = sorted(tiles, key=lambda k: (k['bounds']['top'], k['bounds']['left']))
    return sorted_tiles


def convert_mz_id_to_db_id(mz_id):
    # drop the negative sign, if present and start number with 1 instead.
    # start positive numbers with 2 so that positive and negative numbers are both of the same length (20) and remain unique.
    if mz_id.startswith('-'):
        mz_id = '1' + mz_id.replace('-', '')
    else:
        mz_id = '2' + mz_id

    mz_id_string = str(mz_id)
    dashboard_id = f'00000000-dddd-{mz_id_string[0:4]}-{mz_id_string[4:8]}-{mz_id_string[8:20]}'

    return dashboard_id


def get_dashboard_template(env, token):
    dashboard_template_id = '00000000-dddd-bbbb-ffff-000000000001'
    endpoint = '/api/config/v1/dashboards'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{dashboard_template_id}', token)
    dashboard_template = json.loads(r.text)
    # for tile in dashboard_template.get('tiles'):
    #     print(f'Tiles top/left: {tile["bounds"]["top"]},{tile["bounds"]["left"]}')
    return dashboard_template


def get_entity_type_list(management_zone_name, mz_coverage_dict):
    entity_type_list = []
    for entity_type in entity_types_of_interest:
        count = mz_coverage_dict.get(management_zone_name).get(entity_type)
        if count > 0:
            entity_type_list.append(entity_type)

    return entity_type_list


def get_mz_coverage_for_entity_type(env, token, entity_type, mz_coverage_dict):
    # Skip special entity types covered by a "parent" entity:
    # Database/External services will be counted when the SERVICE entity type is processed
    if entity_type == 'DATABASE_SERVICE' or entity_type == 'EXTERNAL_SERVICE':
        return

    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    raw_params = f'&entitySelector={entity_selector}&fields=managementZones'
    if entity_type == 'SERVICE':
        # raw_params += ',properties.serviceType,properties.isExternalService'
        raw_params += ',properties'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            management_zone_list = inner_entities_json.get('managementZones')
            if management_zone_list:
                if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('serviceType') == 'DATABASE_SERVICE' and 'DATABASE_SERVICE' in entity_types_of_interest:
                    increment_mz_coverage_dict_counts('DATABASE_SERVICE', management_zone_list, mz_coverage_dict)
                else:
                    if entity_type == 'SERVICE' and inner_entities_json.get('properties').get('isExternalService') and inner_entities_json.get('properties').get('agentTechnologyType') == 'N/A' and inner_entities_json.get('properties').get('publicDomainName') and 'EXTERNAL_SERVICE' in entity_types_of_interest:
                        # print(entity_type, inner_entities_json.get('properties'), management_zone_list)
                        increment_mz_coverage_dict_counts('EXTERNAL_SERVICE', management_zone_list, mz_coverage_dict)
                    else:
                        increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict)


def increment_mz_coverage_dict_counts(entity_type, management_zone_list, mz_coverage_dict):
    for management_zone in management_zone_list:
        mz_name = management_zone.get('name')
        if mz_name:
            # print(mz_name, entity_type, management_zone)
            try:
                mz_coverage_dict[mz_name][entity_type] += 1
            except KeyError:
                mz_coverage_dict[mz_name][entity_type] = 0


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    _, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)


if __name__ == '__main__':
    main()
