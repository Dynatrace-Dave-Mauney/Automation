import copy
import glob
import json
import os
import shutil
import yaml
from inspect import currentframe

from Reuse import dynatrace_api

env_name = 'Prod'
# env_name = 'Personal'
# env_name = 'Demo'

# OLD:
# env_name = 'Upper'
# env_name = 'Lower'
# env_name = 'PreProd'
# env_name = 'Sandbox'
# env_name = 'Dev'

tenant = os.getenv(f'DYNATRACE_{env_name.upper()}_TENANT')
env = f'https://{tenant}.live.dynatrace.com'
token = os.getenv(f'DYNATRACE_AUTOMATION_REPORTING_{env_name.upper()}_TOKEN')

PREFIX = f'{env_name}:'
DASHBOARD_CUSTOM_PATH = f'Custom/Overview-{env_name}'
DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'

OWNER = os.environ.get('DYNATRACE_DASHBOARD_OWNER', 'nobody@example.com')
# OWNER = 'nobody@example.com'
# OWNER = 'dave.mauney@dynatrace.com'

SHARED = True
PRESET = True
MENU_PRESET = True

skip_file_name_list = [
    '00000000-dddd-bbbb-ffff-000000000015.json',
    '00000000-dddd-bbbb-ffff-000000000016.json',
    '00000000-dddd-bbbb-ffff-000000000022.json',
    '00000000-dddd-bbbb-ffff-000000000023.json',
    '00000000-dddd-bbbb-ffff-000000000024.json',
    '00000000-dddd-bbbb-ffff-000000000025.json',
    '00000000-dddd-bbbb-ffff-000000000026.json',
    '00000000-dddd-bbbb-ffff-000000000027.json',
    '00000000-dddd-bbbb-ffff-000000000028.json',
    '00000000-dddd-bbbb-ffff-000000000029.json',
    '00000000-dddd-bbbb-ffff-000000000030.json',
    '00000000-dddd-bbbb-ffff-000000000031.json',
    '00000000-dddd-bbbb-ffff-000000000032.json',
    '00000000-dddd-bbbb-ffff-000000000038.json',
    '00000000-dddd-bbbb-ffff-000000000046.json',
    '00000000-dddd-bbbb-ffff-000000000050.json',
    '00000000-dddd-bbbb-ffff-000000000051.json',
    '00000000-dddd-bbbb-ffff-000000000052.json',
    '00000000-dddd-bbbb-ffff-000000000053.json',
    '00000000-dddd-bbbb-ffff-000000000054.json',
    '00000000-dddd-bbbb-ffff-000000000058.json',
    '00000000-dddd-bbbb-ffff-000000000060.json',
    '00000000-dddd-bbbb-ffff-000000000061.json',
    '00000000-dddd-bbbb-ffff-000000000062.json',
    '00000000-dddd-bbbb-ffff-000000000063.json',
    '00000000-dddd-bbbb-ffff-000000000064.json',
    '00000000-dddd-bbbb-ffff-000000000065.json',
    '00000000-dddd-bbbb-ffff-000000000066.json',
    '00000000-dddd-bbbb-ffff-000000000068.json',
    '00000000-dddd-bbbb-ffff-000000000071.json',
    # '00000000-dddd-bbbb-ffff-000000000072.json',
    # '00000000-dddd-bbbb-ffff-000000000077.json',
    # '00000000-dddd-bbbb-ffff-000000000078.json',
    # '00000000-dddd-bbbb-ffff-000000000079.json',
    # '00000000-dddd-bbbb-ffff-000000000080.json',
    # '00000000-dddd-bbbb-ffff-000000000081.json',
    # '00000000-dddd-bbbb-ffff-000000000082.json',
    # '00000000-dddd-bbbb-ffff-000000000083.json',
    # '00000000-dddd-bbbb-ffff-000000000084.json',
    # '00000000-dddd-bbbb-ffff-000000000085.json',
    # '00000000-dddd-bbbb-ffff-000000000086.json',
    # '00000000-dddd-bbbb-ffff-000000000087.json',
    # '00000000-dddd-bbbb-ffff-000000000088.json',
    # '00000000-dddd-bbbb-ffff-000000000089.json',
    # '00000000-dddd-bbbb-ffff-000000000090.json',
    # '00000000-dddd-bbbb-ffff-000000000091.json',
    # '00000000-dddd-bbbb-ffff-000000000092.json',
    # '00000000-dddd-bbbb-ffff-000000000093.json',
    # '00000000-dddd-bbbb-ffff-000000000094.json',
    # '00000000-dddd-bbbb-ffff-000000000095.json',
    # '00000000-dddd-bbbb-ffff-000000000096.json',
    # '00000000-dddd-bbbb-ffff-000000000097.json',
    # '00000000-dddd-bbbb-ffff-000000000098.json',
    '00000000-dddd-bbbb-ffff-000000000122.json',
    '00000000-dddd-bbbb-ffff-000000000123.json',
    '00000000-dddd-bbbb-ffff-000000000131.json',
    '00000000-dddd-bbbb-ffff-000000000132.json',
    '00000000-dddd-bbbb-ffff-000000000133.json',
    '00000000-dddd-bbbb-ffff-000000000134.json',
    '00000000-dddd-bbbb-ffff-000000000135.json',
    '00000000-dddd-bbbb-ffff-000000000136.json',
    '00000000-dddd-bbbb-ffff-000000000137.json',
    '00000000-dddd-bbbb-ffff-000000000138.json',
    '00000000-dddd-bbbb-ffff-000000000139.json',
    '00000000-dddd-bbbb-ffff-000000000140.json',
    '00000000-dddd-bbbb-ffff-000000000141.json',
    '00000000-dddd-bbbb-ffff-000000000142.json',
    '00000000-dddd-bbbb-ffff-000000000143.json',
    '00000000-dddd-bbbb-ffff-000000000144.json',
    '00000000-dddd-bbbb-ffff-000000000145.json',
    '00000000-dddd-bbbb-ffff-000000000146.json',
    '00000000-dddd-bbbb-ffff-000000000147.json',
    '00000000-dddd-bbbb-ffff-000000000148.json',
    '00000000-dddd-bbbb-ffff-000000000149.json',
    '00000000-dddd-bbbb-ffff-000000000150.json',
    '00000000-dddd-bbbb-ffff-000000000151.json',
    '00000000-dddd-bbbb-ffff-000000000152.json',
    '00000000-dddd-bbbb-ffff-000000000153.json',
    '00000000-dddd-bbbb-ffff-000000000154.json',
    '00000000-dddd-bbbb-ffff-000000000155.json',
    '00000000-dddd-bbbb-ffff-000000000156.json',
    '00000000-dddd-bbbb-ffff-000000000157.json',
    '00000000-dddd-bbbb-ffff-000000000158.json',
    '00000000-dddd-bbbb-ffff-000000000806.json',
    '00000000-dddd-bbbb-ffff-000000000807.json',
    '00000000-dddd-bbbb-ffff-000000001000.json',
    '00000000-dddd-bbbb-ffff-000000001001.json',
    '00000000-dddd-bbbb-ffff-000000001002.json',
    '00000000-dddd-bbbb-ffff-000000001003.json',
    '00000000-dddd-bbbb-ffff-000000001004.json',
    '00000000-dddd-bbbb-ffff-000000001005.json',
    '00000000-dddd-bbbb-ffff-000000001006.json',
    '00000000-dddd-bbbb-ffff-000000001007.json',
    '00000000-dddd-bbbb-ffff-000000001008.json',
    '00000000-dddd-bbbb-ffff-000000001009.json',
    '00000000-dddd-bbbb-ffff-000000001010.json',
    '00000000-dddd-bbbb-ffff-000000001011.json',
    '00000000-dddd-bbbb-ffff-000000001012.json',
    '00000000-dddd-bbbb-ffff-000000001013.json',
    '00000000-dddd-bbbb-ffff-000000001014.json',
    '00000000-dddd-bbbb-ffff-000000001015.json',
    '00000000-dddd-bbbb-ffff-000000001016.json',
    '00000000-dddd-bbbb-ffff-000000001017.json',
    '00000000-dddd-bbbb-ffff-000000001018.json',
    '00000000-dddd-bbbb-ffff-000000001019.json',
    '00000000-dddd-bbbb-ffff-000000001020.json',
    '00000000-dddd-bbbb-ffff-000000001021.json',
    '00000000-dddd-bbbb-ffff-000000001022.json',
    '00000000-dddd-bbbb-ffff-000000001023.json',
    '00000000-dddd-bbbb-ffff-000000001024.json',
    '00000000-dddd-bbbb-ffff-000000001025.json',
    '00000000-dddd-bbbb-ffff-000000001102.json',
    '00000000-dddd-bbbb-ffff-000000001103.json',
    '00000000-dddd-bbbb-ffff-000000001104.json',
    '00000000-dddd-bbbb-ffff-000000001105.json',
    '00000000-dddd-bbbb-ffff-000000001106.json',
    '00000000-dddd-bbbb-ffff-000000001107.json',
    '00000000-dddd-bbbb-ffff-000000001108.json',
    '00000000-dddd-bbbb-ffff-000000001109.json',
    '00000000-dddd-bbbb-ffff-000000001110.json',
    '00000000-dddd-bbbb-ffff-000000001111.json',
    '00000000-dddd-bbbb-ffff-000000001112.json',
    '00000000-dddd-bbbb-ffff-000000001113.json',
    '00000000-dddd-bbbb-ffff-000000001114.json',
    '00000000-dddd-bbbb-ffff-000000001115.json',
    '00000000-dddd-bbbb-ffff-000000001116.json',
    '00000000-dddd-bbbb-ffff-000000001117.json',
    '00000000-dddd-bbbb-ffff-000000001118.json',
    '00000000-dddd-bbbb-ffff-000000001119.json',
    '00000000-dddd-bbbb-ffff-000000001120.json',
    '00000000-dddd-bbbb-ffff-000000001121.json',
    '00000000-dddd-bbbb-ffff-000000001122.json',
    '00000000-dddd-bbbb-ffff-000000001123.json',
    '00000000-dddd-bbbb-ffff-000000001124.json',
    '00000000-dddd-bbbb-ffff-000000001125.json',

]

# WEB_APPLICATION_TAGS = ['Web Application Name']
#
# SERVICE_TAGS = [
#     'azure.location',
#     'azure.resource.group',
#     'azure.subscription',
#     'dt.host_group.id',
#     'Host Group',
#     'IIS App Pool',
#     'OS',
#     'primary_tags.app',
#     'primary_tags.env',
#     'primary_tags.function',
#     'primary_tags.tier',
#     'primary_tags.zone',
#     'Process Group Name',
#     'Security Context',
#     'Service Name',
#     'Service Topology Type',
#     'Technology',
# ]
#
# DATABASE_SERVICE_TAGS = [
#     'Host Group',
#     'OS',
#     'Process Group Name',
#     'Security Context',
#     'Service Name',
#     'Service Topology Type',
#     'Technology',
# ]
#
# PROCESS_GROUP_TAGS = [
#     'Geolocation',
#     'Host Group',
#     'IIS App Pool',
#     'OS',
#     'Process Group Name',
#     'Security Context',
#     'Technology',
# ]
#
# HOST_TAGS = [
#     '[Azure]APP',
#     '[Azure]App',
#     '[Azure]application',
#     '[Azure]Application',
#     '[Azure]Backup',
#     '[Azure]BO',
#     '[Azure]BU',
#     '[Azure]Category',
#     '[Azure]CC',
#     '[Azure]CI',
#     '[Azure]CreateBy',
#     '[Azure]DATASEN',
#     '[Azure]DR TIER',
#     '[Azure]ENV',
#     '[Azure]FUNDMETHOD',
#     '[Azure]FundMethod',
#     '[Azure]John Vona TS',
#     '[Azure]Name',
#     '[Azure]Patch Schedule',
#     '[Azure]Patch_Schedule',
#     '[Azure]Patchschedule',
#     '[Azure]PatchSchedule',
#     '[Azure]patchschedule',
#     '[Azure]POC',
#     '[Azure]RequestType',
#     '[Azure]SVC',
#     '[Azure]Vendor',
#     '[Azure]VER',
#     '[Environment]primary_tags.app',
#     '[Environment]primary_tags.env',
#     '[Environment]primary_tags.function',
#     '[Environment]primary_tags.infra',
#     '[Environment]primary_tags.tier',
#     '[Environment]primary_tags.zone',
#     'Geolocation',
#     'Host Group',
#     'Host Name',
#     'IIS App Pool',
#     'IP Address',
#     'OS',
#     'Security Context',
#     'Technology',
#     'verified',
# ]
#
# KUBERNETES_TAGS = [
# ]
#
# IIS_TAGS = ['IIS App Pool', 'IIS Role Name']

WEB_APPLICATION_TAGS = []
SERVICE_TAGS = []
DATABASE_SERVICE_TAGS = []
PROCESS_GROUP_TAGS = []
HOST_TAGS = []
KUBERNETES_TAGS = []
IIS_TAGS = []

WEB_APPLICATION_FILTERS = ['APPLICATION_INJECTION_TYPE']
SERVICE_FILTERS = ['SERVICE_TYPE']
DATABASE_SERVICE_FILTERS = ['DATABASE_VENDOR']
PROCESS_GROUP_FILTERS = []
HOST_FILTERS = ['HOST_MONITORING_MODE', 'HOST_VIRTUALIZATION_TYPE', 'OS_TYPE']
CUSTOM_DEVICE_FILTERS = ['CUSTOM_DIMENSION:Custom Device']

hasMobile = False

hasManagementZoneMarkdown = True

confirmation_required = False
remove_directory_at_startup = True

use_yaml_for_dynamic_tag_filters = True


def customize_dashboards():
    print(f'owner:       {OWNER}')
    print(f'prefix:      "{PREFIX}"')
    print(f'shared:      {SHARED}')
    print(f'preset:      {PRESET}')
    print(f'menu preset: {MENU_PRESET}')

    confirm('Customize dashboards from ' + DASHBOARD_TEMPLATE_PATH + ' to ' + DASHBOARD_CUSTOM_PATH)
    initialize()

    if use_yaml_for_dynamic_tag_filters:
        load_tag_filters_from_yaml()

    for filename in glob.glob(DASHBOARD_TEMPLATE_PATH + '/00000000-*'):
        base_name = os.path.basename(filename)
        # print(filename)
        if base_name not in skip_file_name_list:
            with open(filename, 'r', encoding='utf-8') as f:
                dashboard = f.read()
                new_dashboard = customize_dashboard(dashboard)
                pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
                name = new_dashboard.get('dashboardMetadata').get('name')
                if hasMobile or (not hasMobile and 'Mobile' not in name):
                    output_filename = DASHBOARD_CUSTOM_PATH + '/' + base_name
                    with open(output_filename, 'w', encoding='utf-8') as outfile:
                        outfile.write(pretty_new_dashboard)


def customize_dashboard(dashboard):
    # print(dashboard)
    dashboard = dashboard.replace('{{.tenant}}', tenant)
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    dashboard_id = dashboard_json.get('id')
    name = dashboard_json.get('dashboardMetadata').get('name')
    # print(dashboard_id, name)

    filters = []
    if ': Overview' in name:
        # print(f'Overview in {name}')
        if not hasMobile:
            tiles = dashboard_json.get('tiles')
            app_markdown = tiles[0].get('markdown').replace('Web Apps', 'Web Applications').replace(' / [Mobile Apps](#dashboard;id=00000000-dddd-bbbb-ffff-000000000003)', '')
            new_dashboard_json['tiles'][0]['markdown'] = app_markdown
        if hasManagementZoneMarkdown:
            tiles = dashboard_json.get('tiles')
            for tile in tiles:
                if tile.get('name') == 'Management Zone Overview Links Markdown':
                    print('Modified the mz markdown tile!')
                    tile['markdown'] = generate_management_zone_markdown()
                    new_dashboard_json['tiles'] = tiles
    else:
        if ': Hosts' in name:
            # print(f'Hosts in {name}')
            for value in HOST_TAGS:
                filters.append('HOST_TAG_KEY:' + value)
            filters.extend(HOST_FILTERS)
        else:
            # if ': Processes' in name or ': Java' in name or ': .NET' in name or ': Tomcat' in name or ': WebLogic' in name or ': WebSphere' in name:
            if ': Processes' in name or ': Java' in name or ': .NET' in name or ': Tomcat' in name:
                # print(f'Processes or Process Technology in {name}')
                for value in PROCESS_GROUP_TAGS:
                    filters.append('PROCESS_GROUP_INSTANCE_TAG_KEY:' + value)
                filters.extend(PROCESS_GROUP_FILTERS)
                if not (': Processes' in name or ': .NET' in name):
                    try:
                        filters.remove('PROCESS_GROUP_INSTANCE_TAG_KEY:IIS App Pool')
                    except:
                        pass
            else:
                if ': Web Applications' in name:
                    # print(f'Web Applications in {name}')
                    for value in WEB_APPLICATION_TAGS:
                        filters.append('APPLICATION_TAG_KEY:' + value)
                    filters.extend(WEB_APPLICATION_FILTERS)
                else:
                    if ': Service' in name:
                        # print(f'Service in {name}')
                        for value in SERVICE_TAGS:
                            filters.append('SERVICE_TAG_KEY:' + value)
                        filters.extend(SERVICE_FILTERS)
                    else:
                        if ': Databases' in name:
                            # print(f'Databases in {name}')
                            for value in DATABASE_SERVICE_TAGS:
                                filters.append('SERVICE_TAG_KEY:' + value)
                            filters.extend(DATABASE_SERVICE_FILTERS)
                        else:
                            if ': Network' in name:
                                # print(f'Network in {name}')
                                if 'Host' in name:
                                    # print('Host in name')
                                    for value in HOST_TAGS:
                                        filters.append('HOST_TAG_KEY:' + value)
                                    filters.extend(HOST_FILTERS)
                                else:
                                    if 'Process' in name:
                                        # print(f'Process in *{name}')
                                        for value in PROCESS_GROUP_TAGS:
                                            filters.append('PROCESS_GROUP_INSTANCE_TAG_KEY:' + value)
                                        filters.extend(PROCESS_GROUP_FILTERS)
                            else:
                                # if 'DataPower' in name or 'F5' in name or 'IBM MQ' in name or 'SAP Hana' in name:
                                if 'DataPower' in name or 'F5' in name or 'SAP Hana' in name:
                                    # print(f'Extension in *{name}')
                                    # print('Adding custom device filter...')
                                    filters.extend(CUSTOM_DEVICE_FILTERS)

    if filters:
        new_dashboard_json['dashboardMetadata']['dynamicFilters'] = {}
        new_dashboard_json['dashboardMetadata']['dynamicFilters']['filters'] = filters
    if PREFIX == '':
        name = name.replace('TEMPLATE: ', '')
    else:
        name = name.replace('TEMPLATE:', PREFIX)
    new_dashboard_json['dashboardMetadata']['name'] = name
    new_dashboard_json['dashboardMetadata']['owner'] = OWNER
    new_dashboard_json['dashboardMetadata']['shared'] = SHARED

    if '00000000-dddd-bbbb-ffff-000000000001' in new_dashboard_json['id']:
        new_dashboard_json['dashboardMetadata']['preset'] = MENU_PRESET
    else:
        new_dashboard_json['dashboardMetadata']['preset'] = PRESET

    return new_dashboard_json


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + DASHBOARD_CUSTOM_PATH + ' directory will now be removed to prepare for the conversion.')
        remove_directory(DASHBOARD_CUSTOM_PATH)

    if not os.path.isdir(DASHBOARD_CUSTOM_PATH):
        make_directory(DASHBOARD_CUSTOM_PATH)


def remove_directory(path):
    # print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    # print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    # print('confirm(' + message + ')')
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_linenumber())


def get_linenumber():
    # print('get_linenumber()')
    cf = currentframe()
    return cf.f_back.f_lineno


def load_tag_filters_from_yaml():
    global WEB_APPLICATION_TAGS
    global SERVICE_TAGS
    global PROCESS_GROUP_TAGS
    global HOST_TAGS
    global KUBERNETES_TAGS
    global DATABASE_SERVICE_TAGS
    global IIS_TAGS

    input_filename = f'dynamic_tag_filters_{env_name}.yaml'

    try:
        yaml_dict = read_yaml(input_filename)
    except FileNotFoundError as e:
        print(f'YAML configuration file {input_filename} was not found...aborting')
        exit(1)

    WEB_APPLICATION_TAGS = yaml_dict.get('APPLICATION', [])
    SERVICE_TAGS = yaml_dict.get('SERVICE', [])
    PROCESS_GROUP_TAGS = yaml_dict.get('PROCESS_GROUP', [])
    HOST_TAGS = yaml_dict.get('HOST', [])
    kubernetes_cluster_tags = yaml_dict.get('KUBERNETES_CLUSTER', [])
    kubernetes_node_tags = yaml_dict.get('KUBERNETES_NODE', [])
    kubernetes_service_tags = yaml_dict.get('KUBERNETES_SERVICE', [])
    # print(kubernetes_service_tags, kubernetes_cluster_tags, kubernetes_node_tags)
    KUBERNETES_TAGS = kubernetes_cluster_tags
    if kubernetes_node_tags:
        KUBERNETES_TAGS.extend(kubernetes_cluster_tags)
    if kubernetes_service_tags:
        KUBERNETES_TAGS.extend(kubernetes_service_tags)
    DATABASE_SERVICE_TAGS = yaml_dict.get('DATABASE_SERVICE', [])


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def generate_management_zone_markdown():
    endpoint = '/api/config/v1/managementZones'
    management_zone_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    markdown = 'Management Zone Overview Links\n\n'

    mz_markdown_dict = {}
    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            mz_id = inner_management_zone_json.get('id')
            mz_name = inner_management_zone_json.get('name')
            dashboard_id = convert_mz_id_to_db_id(mz_id)
            mz_markdown_dict[mz_name] = {'mz_id': mz_id, 'dashboard_id': dashboard_id}

    for mz_name in sorted(mz_markdown_dict.keys()):
        dashboard_id = mz_markdown_dict[mz_name]['dashboard_id']
        mz_id = mz_markdown_dict[mz_name]['mz_id']
        markdown += f'[{mz_name}](#dashboard;id={dashboard_id};gf={mz_id})  \n'

    return markdown


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


def main():
    customize_dashboards()


if __name__ == '__main__':
    main()
