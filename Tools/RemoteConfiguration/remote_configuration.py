import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

host_lookup = {}


def process(env, main_token, remote_config_token):
    pass
    # clear_some_tier_0_tags(env, main_token, remote_config_token)
    # clear_some_tier_1_tags(env, main_token, remote_config_token)
    # clear_some_tier_tags(env, main_token, remote_config_token)

    # set_some_tier_0_tags(env, main_token, remote_config_token)
    # set_some_tier_1_tags(env, main_token, remote_config_token)
    # set_some_tier_2_tags(env, main_token, remote_config_token)

    # clear_all_tier_0_tags(env, main_token, remote_config_token)
    # set_all_tier_unset_tags_to_tier_2(env, main_token, remote_config_token)

    # clear_some_network_zone_tags(env, main_token, remote_config_token, 'onprem')

    # set_some_network_zones(env, main_token, remote_config_token, 'azure')
    # set_some_network_zones(env, main_token, remote_config_token, 'onprem')

    # set_some_network_zone_tags(env, main_token, remote_config_token, 'azure')

    get_current_job(env, remote_config_token)
    # get_finished_jobs(env, remote_config_token, True)


def clear_some_tier_0_tags(env, main_token, remote_config_token):
    apps_to_clear = [
    'dsrip',
    'omnicell',
    ]
    host_id_list = []
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            if "'key': 'primary_tags.tier', 'value': '0'" in str(tags):
                app_tag = get_app_tag(tags)
                if app_tag in apps_to_clear:
                    print(f'Removing tier:0 tag for app {app_tag}:', display_name, entity_id)
                    host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'clear', 'primary_tags.tier=0')


def clear_some_tier_tags(env, main_token, remote_config_token):
    tier0_apps_to_clear = [
        'ad-azure-password',
        'adfr-dc-shared',
        'adfs',
        'azure-ad-connect',
        'domain-controller',
        'exchange',
    ]

    tier1_apps_to_clear = [
        'beyond-trust-password-safe',
        'beyondtrust',
        'citrix',
        'net-backup',
        'obix',
        'powerpath',
        'symantec-vip',
        'ukg-kronos-time-attendance-mssn',
    ]

    tier2_apps_to_clear = [
        'cache-server',
        'citrix-federated-authentication-services',
        'digital-marketing',
        'dsrip',
        'dynatrace',
        'eclipse',
        'main-web-site-marketing',
        'msdw',
        'nxlog',
        'pakedge',
        'research-it',
        'scottcare',
        'v4',
    ]
    host_id_list_0 = []
    host_id_list_1 = []
    host_id_list_2 = []

    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            if "'key': 'primary_tags.tier', 'value': '0'" in str(tags):
                app_tag = get_app_tag(tags)
                if app_tag in tier1_apps_to_clear or app_tag in tier2_apps_to_clear:
                    print(f'Removing tier:0 tag for app {app_tag}:', display_name, entity_id)
                    host_id_list_0.append(entity_id)
            if "'key': 'primary_tags.tier', 'value': '1'" in str(tags):
                app_tag = get_app_tag(tags)
                if app_tag in tier0_apps_to_clear or app_tag in tier2_apps_to_clear:
                    print(f'Removing tier:1 tag for app {app_tag}:', display_name, entity_id)
                    host_id_list_1.append(entity_id)
            if "'key': 'primary_tags.tier', 'value': '2'" in str(tags):
                app_tag = get_app_tag(tags)
                if app_tag in tier0_apps_to_clear or app_tag in tier1_apps_to_clear:
                    print(f'Removing tier:2 tag for app {app_tag}:', display_name, entity_id)
                    host_id_list_2.append(entity_id)

    # print('Tier 0 Clears')
    # for key in host_id_list_0:
    #     print(key)
    #
    # print('')
    # print('Tier 1 Clears')
    # for key in host_id_list_1:
    #     print(key)
    #
    # print('')
    # print('Tier 2 Clears')
    # for key in host_id_list_2:
    #     print(key)


    import time
    if host_id_list_0:
        post_host_tag_job(env, remote_config_token, host_id_list_0, 'clear', 'primary_tags.tier=0')
        time.sleep(60)
    if host_id_list_1:
        post_host_tag_job(env, remote_config_token, host_id_list_1, 'clear', 'primary_tags.tier=1')
        time.sleep(60)
    if host_id_list_2:
        post_host_tag_job(env, remote_config_token, host_id_list_2, 'clear', 'primary_tags.tier=2')


def clear_some_network_zone_tags(env, main_token, remote_config_token, zone):
    hosts_to_clear = [
        'SPYDBMQ28001',
        'SPYDICRPF28002',
        'SPYDICRPF28003',
        'SPYDICRPF28004',
        'SPYDICRPF28005',
        'SPYDICRPF28006',
        'SPYDICRPF28007',
        'SPYDICRPF28008',
        'SPYDICRPF28009',
        'SPYDICRPM28001',
        'SPYDICRPM28002',
        'SPYDICRPM28003',
        'SPYDICRPM28004',
        'SPYDICRPM28005',
        'SPYDICRPM28006',
        'SPYDICRPM28007',
        'SPYDICRPM28008',
        'SPYDICRPM28009',
        'SPYDICRPM28010',
        'SPYDICRPM28011',
        'SPYDICRPM28012',
        'SPYDICRPM28013',
        'SPYDICRPM28014',
        'SPYDICRPM28015',
        'SPYDICRPM28016',
        'SPYDICRPM28017',
        'SPYDICRPM28018',
        'SPYDICRPM28019',
        'SPYDICRPM28020',
        'SPYDICRPM28021',
        'SPYDICRPM28022',
        'SPYDICRPM28023',
        'SPYDICRPM28024',
        'SPYDICRPM28025',
        'SPYDICRPM28026',
        'SPYDICRPM28027',
        'SPYDICRPM28028',
        'SPYDICRPM28029',
        'SPYHIEDBSMT28002',
        'SPYHIEDICRT28002',
        'SPYHIEIDMST28002',
        'SPYHIEMDSCT28002',
        'SPYHIEMDSCT28003',
        'SPYIDMQ28001',
        'SPYMDSCQ28001',
        'SPYRDBMD28001',
        'SPYRDBMP28002',
        'SPYRDBMP28003',
        'SPYRDBMP28004',
        'SPYRDBMQ28001',
        'SPYRDBMSP28001',
        'SPYRDBMSP28002',
        'SPYRDICRP28003',
        'SPYRDICRP28004',
        'SPYRDICRP28005',
        'SPYRDICRQ28001',
        'SPYRIDMP28001',
        'SPYRIDMP28002',
        'SPYRIDMQ28001',
        'SPYRIDPP28001',
        'SPYRIDPP28002',
        'SPYRIDXP28001',
        'SPYRIDXP28002',
        'SPYRMAPP28001',
        'SPYRMAPP28002',
        'SPYRMAPP28003',
        'SPYRMAPP28004',
        'SPYRMNP28001',
        'SPYRMNP28002',
        'SPYRNFIP28001',
        'SPYRNFIP28002',
        'SPYRSKYP28001',
        'fhirdevapi.mountsinai.org',
        'fhirtestapi.mountsinai.org',
    ]
    hosts_to_clear = [
        'zeusnwapmnp001.mssmcampus.mssm.edu',
    ]
    hosts_to_clear = [
        'zeuspwaddc001.msnyuhealth.org',
        'zeuspwaddc002.msnyuhealth.org',
        'zeuspwapsct001.msnyuhealth.org',
        'zeuspwapsctc001.msnyuhealth.org',
        'zeuspwctxbed002.msnyuhealth.org',
    ]
    host_id_list = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            if display_name in hosts_to_clear:
                print(f'Removing zone:{zone} tag:', display_name, entity_id)
                host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'clear', f'primary_tags.zone={zone}')


def set_some_tier_0_tags(env, main_token, remote_config_token):
    apps_to_set = [
        'active-directory',
        'ad-azure-password',
        'ad-utility-server',
        'adfr-dc-shared',
        'adfs',
        'azure-ad-connect',
        'domain-controller',
        'exchange',
    ]
    apps_to_set = [
        'beyondtrust',
        'beyond-trust-password-safe',
        'net-backup',
        'powerpath',
        'symantec-vip',
        'ukg-kronos-time-attendance-mssn'
    ]

    host_id_list = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            app_tag = get_app_tag(tags)
            if app_tag in apps_to_set:
                print(f'Setting tier:0 tag for app {app_tag}:', display_name, entity_id)
                host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'set', 'primary_tags.tier=0')


def set_some_network_zone_tags(env, main_token, remote_config_token, zone):
    hosts_to_set = [
        'SPYDBMQ28001',
        'SPYDICRPF28002',
        'SPYDICRPF28003',
        'SPYDICRPF28004',
        'SPYDICRPF28005',
        'SPYDICRPF28006',
        'SPYDICRPF28007',
        'SPYDICRPF28008',
        'SPYDICRPF28009',
        'SPYDICRPM28001',
        'SPYDICRPM28002',
        'SPYDICRPM28003',
        'SPYDICRPM28004',
        'SPYDICRPM28005',
        'SPYDICRPM28006',
        'SPYDICRPM28007',
        'SPYDICRPM28008',
        'SPYDICRPM28009',
        'SPYDICRPM28010',
        'SPYDICRPM28011',
        'SPYDICRPM28012',
        'SPYDICRPM28013',
        'SPYDICRPM28014',
        'SPYDICRPM28015',
        'SPYDICRPM28016',
        'SPYDICRPM28017',
        'SPYDICRPM28018',
        'SPYDICRPM28019',
        'SPYDICRPM28020',
        'SPYDICRPM28021',
        'SPYDICRPM28022',
        'SPYDICRPM28023',
        'SPYDICRPM28024',
        'SPYDICRPM28025',
        'SPYDICRPM28026',
        'SPYDICRPM28027',
        'SPYDICRPM28028',
        'SPYDICRPM28029',
        'SPYHIEDBSMT28002',
        'SPYHIEDICRT28002',
        'SPYHIEIDMST28002',
        'SPYHIEMDSCT28002',
        'SPYHIEMDSCT28003',
        'SPYIDMQ28001',
        'SPYMDSCQ28001',
        'SPYRDBMD28001',
        'SPYRDBMP28002',
        'SPYRDBMP28003',
        'SPYRDBMP28004',
        'SPYRDBMQ28001',
        'SPYRDBMSP28001',
        'SPYRDBMSP28002',
        'SPYRDICRP28003',
        'SPYRDICRP28004',
        'SPYRDICRP28005',
        'SPYRDICRQ28001',
        'SPYRIDMP28001',
        'SPYRIDMP28002',
        'SPYRIDMQ28001',
        'SPYRIDPP28001',
        'SPYRIDPP28002',
        'SPYRIDXP28001',
        'SPYRIDXP28002',
        'SPYRMAPP28001',
        'SPYRMAPP28002',
        'SPYRMAPP28003',
        'SPYRMAPP28004',
        'SPYRMNP28001',
        'SPYRMNP28002',
        'SPYRNFIP28001',
        'SPYRNFIP28002',
        'SPYRSKYP28001',
        'fhirdevapi.mountsinai.org',
        'fhirtestapi.mountsinai.org',
    ]
    hosts_to_set = [
        'zeusnwapmnp001.mssmcampus.mssm.edu',
    ]
    hosts_to_set = [
        'zeuspwaddc001.msnyuhealth.org',
        'zeuspwaddc002.msnyuhealth.org',
        'zeuspwapsct001.msnyuhealth.org',
        'zeuspwapsctc001.msnyuhealth.org',
        'zeuspwctxbed002.msnyuhealth.org',
    ]
    host_id_list = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            if display_name in hosts_to_set:
                print(f'Setting zone:{zone} tag:', display_name, entity_id)
                host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'set', f'primary_tags.zone={zone}')


def clear_some_tier_1_tags(env, main_token, remote_config_token):
    apps_to_clear = [
    '3m',
    '3m-enterprise-crs-application-server',
    '3m-enterprise-hdm-app-prod-server',
    '3m-enterprise-interface-prod-server',
    '3m-enterprise-rep-core-server',
    '3m-enterprise-report-prod-server',
    '3m-enterprise-sql-prod-server',
    '3m-enterprise-web-prod-server',
    'edr',
    'exchange',
    'geviewpoint',
    'qpathe',
    'symantec-vip',
    'ukg-kronos-time-attendance-mssn',
    ]
    apps_to_clear = [
    'ad-azure-password',
    'adfr-dc-shared',
    'azure-ad-connect',
    'exchange',
    ]
    apps_to_clear = [
        'beyondtrust',
        'beyond-trust-password-safe',
        'net-backup',
        'powerpath',
        'symantec-vip',
        'ukg-kronos-time-attendance-mssn'
    ]
    host_id_list = []
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            if "'key': 'primary_tags.tier', 'value': '1'" in str(tags):
                app_tag = get_app_tag(tags)
                if app_tag in apps_to_clear:
                    print(f'Removing tier:1 tag for app {app_tag}:', display_name, entity_id)
                    host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'clear', 'primary_tags.tier=1')

def set_some_tier_1_tags(env, main_token, remote_config_token):
    # apps_to_set = [
    # 	'aig',
    # 	'beyond-trust-password-safe',
    # 	'ge-pacs',
    # 	'sectra',
    # 	'ukg-kronos-time-&-attendance-mssn',
    # ]
    # apps_to_set = [
    #     'qpathe',
    #     'symantec-vip',
    #     'ukg-kronos-time-attendance-mssn',
    # ]
    apps_to_set = [
        'citrix',
        'obix',
    ]

    host_id_list = []
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            app_tag = get_app_tag(tags)
            if app_tag in apps_to_set:
                print(f'Setting tier:1 tag for app {app_tag}:', display_name, entity_id)
                host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'set', 'primary_tags.tier=1')

def set_some_tier_2_tags(env, main_token, remote_config_token):
    apps_to_set = [
        'pakedge',
        'scottcare',
    ]

    host_id_list = []
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            app_tag = get_app_tag(tags)
            if app_tag in apps_to_set:
                print(f'Setting tier:2 tag for app {app_tag}:', display_name, entity_id)
                host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'set', 'primary_tags.tier=2')

def set_all_tier_unset_tags_to_tier_2(env, main_token, remote_config_token):
    host_id_list = []
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            tags = inner_entities_json.get('tags', [])
            tier_tag = get_tier_tag(tags)
            if not tier_tag or tier_tag == '0':
                print(f'Setting tier:2 tag:', tier_tag, display_name, entity_id)
                host_id_list.append(entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'set', 'primary_tags.tier=2')

def clear_all_tier_0_tags(env, main_token, remote_config_token):
    host_id_list = []
    endpoint = '/api/v2/entities'
    # raw_params = 'pageSize=4000&entitySelector=type(HOST)&to=-5m&fields=properties,tags,managementZones'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=tags'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            properties = inner_entities_json.get('properties')
            tags = inner_entities_json.get('tags', [])
            if "'key': 'primary_tags.tier', 'value': '0'" in str(tags):
                print('Tier0:', display_name, entity_id)
                host_id_list.append(entity_id)
            # host_lookup[display_name] = entity_id
            else:
                print('Tier1:', display_name, entity_id)

    post_host_tag_job(env, remote_config_token, host_id_list, 'clear', 'primary_tags.tier=0')


def set_some_network_zones(env, main_token, remote_config_token, network_zone):
    hosts_to_change = [
    'SPYDBMQ28001',
    'SPYDICRPF28002',
    'SPYDICRPF28003',
    'SPYDICRPF28004',
    'SPYDICRPF28005',
    'SPYDICRPF28006',
    'SPYDICRPF28007',
    'SPYDICRPF28008',
    'SPYDICRPF28009',
    'SPYDICRPM28001',
    'SPYDICRPM28002',
    'SPYDICRPM28003',
    'SPYDICRPM28004',
    'SPYDICRPM28005',
    'SPYDICRPM28006',
    'SPYDICRPM28007',
    'SPYDICRPM28008',
    'SPYDICRPM28009',
    'SPYDICRPM28010',
    'SPYDICRPM28011',
    'SPYDICRPM28012',
    'SPYDICRPM28013',
    'SPYDICRPM28014',
    'SPYDICRPM28015',
    'SPYDICRPM28016',
    'SPYDICRPM28017',
    'SPYDICRPM28018',
    'SPYDICRPM28019',
    'SPYDICRPM28020',
    'SPYDICRPM28021',
    'SPYDICRPM28022',
    'SPYDICRPM28023',
    'SPYDICRPM28024',
    'SPYDICRPM28025',
    'SPYDICRPM28026',
    'SPYDICRPM28027',
    'SPYDICRPM28028',
    'SPYDICRPM28029',
    'SPYHIEDBSMT28002',
    'SPYHIEDICRT28002',
    'SPYHIEIDMST28002',
    'SPYHIEMDSCT28002',
    'SPYHIEMDSCT28003',
    'SPYIDMQ28001',
    'SPYMDSCQ28001',
    'SPYRDBMD28001',
    'SPYRDBMP28002',
    'SPYRDBMP28003',
    'SPYRDBMP28004',
    'SPYRDBMQ28001',
    'SPYRDBMSP28001',
    'SPYRDBMSP28002',
    'SPYRDICRP28003',
    'SPYRDICRP28004',
    'SPYRDICRP28005',
    'SPYRDICRQ28001',
    'SPYRIDMP28001',
    'SPYRIDMP28002',
    'SPYRIDMQ28001',
    'SPYRIDPP28001',
    'SPYRIDPP28002',
    'SPYRIDXP28001',
    'SPYRIDXP28002',
    'SPYRMAPP28001',
    'SPYRMAPP28002',
    'SPYRMAPP28003',
    'SPYRMAPP28004',
    'SPYRMNP28001',
    'SPYRMNP28002',
    'SPYRNFIP28001',
    'SPYRNFIP28002',
    'SPYRSKYP28001',
    'fhirdevapi.mountsinai.org',
    'fhirtestapi.mountsinai.org',
    ]
    # hosts_to_change = [
    #     'CVI-SCOTHL7PROD.msnyuhealth.org',
    #     'zeuspwaddc001.msnyuhealth.org',
    #     'zeuspwaddc002.msnyuhealth.org',
    #     'zeuspwapsct001.msnyuhealth.org',
    #     'zeuspwapsctc001.msnyuhealth.org',
    #     'zeuspwctxbed002.msnyuhealth.org',
    # ]
    hosts_to_change = [
        'SNPTAPPP219001.msnyuhealth.org',
        'app65.itdc.mssm.edu',
    ]
    host_id_list = []
    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(HOST),isMonitoringCandidate(false)&from=-5m&fields=properties'
    params = urllib.parse.quote(raw_params, safe='/,&=?')
    entities_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', main_token, params=params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId', '')
            display_name = inner_entities_json.get('displayName', '')
            properties = inner_entities_json.get('properties')
            current_network_zone = properties.get('networkZone', '')
            if display_name in hosts_to_change:
                print('Network Zone Change (from/to):', display_name, entity_id, current_network_zone, network_zone)
                host_id_list.append(entity_id)

    post_host_network_zone_job(env, remote_config_token, host_id_list, 'set', network_zone)


def get_app_tag(tags):
    app_tag = None
    for tag in tags:
        if "'key': 'primary_tags.app'" in str(tag):
            app_tag = tag.get('value')
            # print(app_tag, tag)

    return app_tag

def get_tier_tag(tags):
    tier_tag = None
    for tag in tags:
        if "'key': 'primary_tags.tier'" in str(tag):
            tier_tag = tag.get('value')

    return tier_tag

    ########################################################################################################
    #                                                                                                      #
    #                                             OBSOLETE                                                 #
    #                                                                                                      #
    ########################################################################################################

    # host_list = [
    # # CUSTOMER
    # 'zeuspwcxnyh001.msnyuhealth.org',
    # # PERSONAL
    # # 'DT-8VBQQV3 accounting_app_prod',
    # ]
    #
    # host_id_list = []
    # for host in host_list:
    # 	host_id = get_host_id(host)
    # 	host_id_list.append(host_id)

    # post_host_tag_job(host_id_list, 'clear', 'primary_tags.app=nyee-user-file-shares')
    # post_host_tag_job(host_id_list, 'clear', 'primary_tags.function=db-sql')
    # get_current_job()

    # get_finished_jobs(env, remote_config_token, True)
    # post_host_tag_job(host_id_list, 'clear', 'primary_tags.zone=azure')
    # post_host_tag_job(host_id_list, 'set', 'primary_tags.zone=notazure')


# def get_host_id(host):
# 	return host_lookup[host]


########################################################################################################
#                                                                                                      #
#                                             USEFUL                                                 #
#                                                                                                      #
########################################################################################################

def post_host_tag_job(env, token, host_id_list, operation, tag):
    endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
    payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "hostTag",
      "operation": f"{operation}",
      "value": f"{tag}"
    }
  ]
}
    payload_dict['entities'] = host_id_list
    payload = json.dumps(payload_dict)
    print(payload)
    # post_validate_payload(payload)
    # exit(9999)
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
    print(r, r.status_code, r.text)


def post_host_network_zone_job(env, token, host_id_list, operation, network_zone):
    endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
    payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "networkZone",
      "operation": f"{operation}",
      "value": f"{network_zone}"
    }
  ]
}
    payload_dict['entities'] = host_id_list
    payload = json.dumps(payload_dict)
    print(payload)
    # post_validate_payload(payload)
    # exit(9999)
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
    print(r, r.status_code, r.text)


def post_validate_payload(env, token, payload):
    endpoint = '/api/v2/oneagents/remoteConfigurationManagement/validator'
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
    print(r, r.status_code, r.text)


def get_current_job(env, token):
    endpoint = '/api/v2/oneagents/remoteConfigurationManagement/current'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    print(r, r.status_code, r.text)
    if r.status_code == 204:
        print('No remote configuration management job is currently running')
    else:
        json_list = r.json()
        print(json_list)
        for json in json_list:
            print(json)


def get_finished_jobs(env, token, most_recent):
    endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    print(r, r.status_code, r.text)
    json_response = r.json()
    print(json_response)
    json_list = json_response.get('jobs')
    for job in json_list:
        job_id = job.get('id')
        get_job(env, token, job_id)
        if most_recent:
            return


def get_job(env, token, job_id):
    endpoint = f'/api/v2/oneagents/remoteConfigurationManagement/{job_id}'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    print(r, r.status_code, r.text)
    json_list = r.json()
    print(json_list)


# OBSOLETE
def post_job(env, token, host_id_list):
    endpoint = '/api/v2/oneagents/remoteConfigurationManagement'
    payload_dict = {
  "entities": [],
  "operations": [
    {
      "attribute": "networkZone",
      "operation": "set",
      "value": "azure"
    }
  ]
}
    payload_dict['entities'] = host_id_list
    payload = json.dumps(payload_dict)
    r = dynatrace_api.post_object(f'{env}{endpoint}', token, payload)
    print(r, r.status_code, r.text)


if __name__ == '__main__':
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'Personal'
    env_name, env, main_token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    # Use a new token later, this is a hack
    configuration_file = 'configurations.yaml'
    remote_config_token = environment.get_configuration('token', configuration_file=configuration_file)

    if not env or not main_token or not remote_config_token:
        print('Env or Token Environment Variable Not Set!')
        exit(1)

    process(env, main_token, remote_config_token)
