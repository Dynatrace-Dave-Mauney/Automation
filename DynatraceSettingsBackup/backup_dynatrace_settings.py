"""
Save Dynatrace settings to individual JSON files and to a single YAML file that can be used to PUT, POST, or DELETE settings later.
Note:  the PUT/POST module is not posted on GitHub as it is extremely "dangerous".
If you have an urgent need for a "restore" capability, contact the author.

Covers:
All Settings 2.0 configurations, based on a full list of schemas returned by the API.
Most settings in the Configuration API spec (which must be downloaded manually and saved as "config_v1_spec3.json").
SLOs, Synthetic Monitors and Synthetic Locations from the Environment APIs (v1/v2).

Token Permissions Required:
"Read configuration: ReadConfig"
"Read settings: settings.read"
"credentialVault.read (Read credential vault entries)" - if you want to save credentials
"DssFileManagement (Mobile symbolication file management)" - if you want to save symbol files (This may be obsolete now).
"""

import copy
import json
import os
import shutil
import yaml
import urllib.parse

from inspect import currentframe

from Reuse import dynatrace_api
from Reuse import environment

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
# env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')

# backup_directory_path = f'../$Output/DynatraceSettingsBackup/{env_name}'
# To help with file names that are too long, use a very short directory name
backup_directory_path = f'/tmp'

settings20_yaml_file_name = 'settings20.yaml'
config_yaml_file_name = 'config.yaml'
environment_yaml_file_name = 'environment.yaml'
confirmation_required = True
long_file_suffix = 0

# Set to False for partial runs (configs only, settings only, etc.)
# OR, just answer "n" when prompted and leave this setting True
remove_directory_at_startup = True

supported_config_endpoints = [
    '/alertingProfiles',
    '/allowedBeaconOriginsForCors',
    '/anomalyDetection/applications',
    '/anomalyDetection/aws',
    '/anomalyDetection/databaseServices',
    '/anomalyDetection/diskEvents',
    '/anomalyDetection/hosts',
    '/anomalyDetection/metricEvents',
    '/anomalyDetection/services',
    '/anomalyDetection/vmware',
    '/applicationDetectionRules',
    '/applicationDetectionRules/hostDetection',
    # '/applicationDetectionRules/order',
    '/applications/mobile',
    '/applications/mobile/{applicationId}/keyUserActions',
    '/applications/mobile/{applicationId}/userActionAndSessionProperties',
    '/applications/web',
    '/applications/web/dataPrivacy',
    '/applications/web/default',
    '/applications/web/default/dataPrivacy',
    '/applications/web/{id}/dataPrivacy',
    '/applications/web/{id}/errorRules',
    '/applications/web/{id}/keyUserActions',
    '/autoTags',
    '/aws/credentials',
    '/aws/credentials/{id}/services',
    '/aws/iamExternalId',
    '/aws/privateLink',
    '/aws/privateLink/allowlistedAccounts',
    '/aws/supportedServices',
    '/azure/credentials',
    '/azure/credentials/{id}/services',
    '/azure/supportedServices',
    # '/calculatedMetrics/log', # Must be turned off if V2 Logging is in use
    '/calculatedMetrics/mobile',
    '/calculatedMetrics/rum',
    '/calculatedMetrics/service',
    '/calculatedMetrics/synthetic',
    '/cloudFoundry/credentials',
    '/conditionalNaming/{type}',
    '/contentResources',
    '/credentials',
    '/dashboards',
    # '/dashboards/{id}/shareSettings', # Not important?
    '/dataPrivacy',
    '/extensions',
    '/extensions/activeGateExtensionModules',
    '/frequentIssueDetection',
    '/geographicRegions/ipAddressMappings',
    '/geographicRegions/ipDetectionHeaders',
    # '/hostgroups/{id}/autoupdate',
    '/hosts/autoupdate',
    # '/hosts/{id}/autoupdate',
    # '/hosts/{id}/monitoring',
    # '/hosts/{id}/technologies',
    '/kubernetes/credentials',
    '/maintenanceWindows',
    '/managementZones',
    '/notifications',
    '/plugins',
    '/plugins/activeGatePluginModules',
    # '/plugins/{id}/endpoints',
    '/remoteEnvironments',
    # '/reports', # Not needed
    '/service/customServices/{technology}',
    # '/service/customServices/{technology}/order', # Endpoint does not support get method
    '/service/detectionRules/FULL_WEB_REQUEST',
    '/service/detectionRules/FULL_WEB_REQUEST/order',
    '/service/detectionRules/FULL_WEB_SERVICE',
    '/service/detectionRules/FULL_WEB_SERVICE/order',
    '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST',
    '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST/order',
    '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE',
    '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE/order',
    '/service/failureDetection/parameterSelection/parameterSets',
    '/service/failureDetection/parameterSelection/rules',
    '/service/failureDetection/parameterSelection/rules/reorderRules',
    '/service/requestAttributes',
    '/service/requestNaming',
    '/service/requestNaming/order',
    '/service/resourceNaming',
    '/technologies',
]

# For Testing, override the official list above
# supported_config_endpoints = [
#     '/alertingProfiles',
#     '/technologies',
# ]

# supported_config_endpoints = [
#     # '/applications/mobile',
#     # '/applications/mobile/{applicationId}/keyUserActions',
#     # '/applications/mobile/{applicationId}/userActionAndSessionProperties',
#     '/applications/web',
#     '/applications/web/dataPrivacy',
#     '/applications/web/default',
#     '/applications/web/default/dataPrivacy',
#     '/applications/web/{id}/dataPrivacy',
#     '/applications/web/{id}/errorRules',
#     '/applications/web/{id}/keyUserActions',
# ]

endpoint_child_keys = {
    '/alertingProfiles': ['values', 'id'],
    '/anomalyDetection/diskEvents': ['values', 'id'],
    '/anomalyDetection/metricEvents': ['values', 'id'],
    '/applicationDetectionRules': ['values', 'id'],
    '/applications/mobile': ['values', 'id'],
    '/applications/web': ['values', 'id'],
    '/autoTags': ['values', 'id'],
    '/aws/credentials': ['values', 'id'],
    '/aws/privateLink/allowlistedAccounts': ['values', 'id'],
    # '/aws/supportedServices': ['services', 'name'],
    '/azure/credentials': ['values', 'id'],
    # '/azure/supportedServices': ['services', 'name'],
    '/calculatedMetrics/mobile': ['values', 'id'],
    '/calculatedMetrics/rum': ['values', 'id'],
    '/calculatedMetrics/service': ['values', 'id'],
    '/calculatedMetrics/synthetic': ['values', 'id'],
    '/credentials': ['credentials', 'id'],
    '/dashboards': ['dashboards', 'id'],
    '/extensions': ['extensions', 'id'],
    # '/extensions/activeGateExtensionModules': ['values', 'id'],
    '/cloudFoundry/credentials': ['values', 'id'],
    '/kubernetes/credentials': ['values', 'id'],
    '/maintenanceWindows': ['values', 'id'],
    '/managementZones': ['values', 'id'],
    '/notifications': ['values', 'id'],
    '/plugins': ['values', 'id'],
    # '/plugins/activeGatePluginModules': ['values', 'id'],
    '/remoteEnvironments': ['values', 'id'],
    '/reports': ['values', 'id'],
    '/service/detectionRules/FULL_WEB_REQUEST': ['values', 'id'],
    '/service/detectionRules/FULL_WEB_SERVICE': ['values', 'id'],
    '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST': ['values', 'id'],
    '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE': ['values', 'id'],
    '/service/failureDetection/parameterSelection/parameterSets': ['values', 'id'],
    '/service/failureDetection/parameterSelection/rules': ['values', 'id'],
    '/service/requestAttributes': ['values', 'id'],
    '/service/requestNaming': ['values', 'id'],
}


def initialize():
    if remove_directory_at_startup:
        message = f'The {backup_directory_path} directory will now be removed to prepare for backup.'
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if proceed:
            remove_directory(backup_directory_path)
            if not os.path.isdir(backup_directory_path):
                make_directory(backup_directory_path)
        else:
            print(f'The {backup_directory_path} directory was not removed for for this backup.')


def remove_directory(path):
    # print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        pass
        # print('Removed the directory %s ' % path)


def make_directory(path):
    # print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        pass
        # print('Successfully created the directory %s ' % path)


def save_configuration_api_settings():
    # print('save_configuration_api_settings()')
    filename = backup_directory_path + '/' + config_yaml_file_name
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}

    yaml_dict = copy.deepcopy(main_template)
    config_list = []

    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        if not process_config_endpoint(endpoint, paths):
            # print(f'Not processing endpoint {endpoint} {supported_config_endpoints}')
            continue

        print(f'processing endpoint {endpoint}')

        if '{' in endpoint:
            process_complex_endpoint(endpoint, paths, config_list)
        else:
            process_simple_endpoint(endpoint, None, config_list)

        yaml_dict['configs'] = config_list

        with open(filename, 'w') as file:
            yaml.dump(yaml_dict, file, sort_keys=False)


def process_config_endpoint(endpoint, paths):
    # Does endpoint allow get method?
    endpoint_dict = paths.get(endpoint)
    methods = list(endpoint_dict.keys())
    if 'get' not in methods:
        # print(f'Endpoint {endpoint} does not allow get method')
        return False

    # # Is endpoint in the "least complex" list?
    # if endpoint not in ['/alertingProfiles', '/allowedBeaconOriginsForCors', '/anomalyDetection/applications', '/anomalyDetection/aws', '/anomalyDetection/databaseServices', '/anomalyDetection/diskEvents', '/anomalyDetection/hosts', '/anomalyDetection/metricEvents', '/anomalyDetection/services', '/anomalyDetection/vmware', '/applicationDetectionRules', '/applicationDetectionRules/hostDetection', '/applicationDetectionRules/order', '/applications/mobile', '/applications/web', '/applications/web/dataPrivacy', '/applications/web/default', '/applications/web/default/dataPrivacy', '/autoTags', '/aws/credentials', '/aws/iamExternalId', '/aws/privateLink', '/aws/privateLink/allowlistedAccounts', '/aws/supportedServices', '/azure/credentials', '/azure/supportedServices', '/calculatedMetrics/log', '/calculatedMetrics/mobile', '/calculatedMetrics/rum', '/calculatedMetrics/service', '/calculatedMetrics/synthetic', '/cloudFoundry/credentials', '/contentResources', '/credentials', '/dashboards', '/dataPrivacy', '/extensions', '/extensions/activeGateExtensionModules', '/frequentIssueDetection', '/geographicRegions/ipAddressMappings', '/geographicRegions/ipDetectionHeaders', '/hosts/autoupdate', '/kubernetes/credentials', '/maintenanceWindows', '/managementZones', '/notifications', '/plugins', '/plugins/activeGatePluginModules', '/remoteEnvironments', '/reports', '/service/detectionRules/FULL_WEB_REQUEST', '/service/detectionRules/FULL_WEB_REQUEST/order', '/service/detectionRules/FULL_WEB_SERVICE', '/service/detectionRules/FULL_WEB_SERVICE/order', '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST', '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST/order', '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE', '/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE/order', '/service/failureDetection/parameterSelection/parameterSets', '/service/failureDetection/parameterSelection/rules', '/service/failureDetection/parameterSelection/rules/reorderRules', '/service/requestAttributes', '/service/requestNaming', '/service/requestNaming/order', '/service/resourceNaming', '/technologies']:
    #     return False
    #
    # # Fails if logging V2+
    # if endpoint == '/calculatedMetrics/log':
    #     return False

    if endpoint in supported_config_endpoints:
        return True
    else:
        return False


def process_simple_endpoint(endpoint, endpoint_child_key, config_list):
    resp = get_config_endpoint(endpoint)
    # print('Children Process...')
    if not endpoint_child_key:
        endpoint_child_key = endpoint_child_keys.get(endpoint)
    if endpoint_child_key:
        if endpoint == '/aws/credentials':
            children = json.loads(resp.text)
        else:
            children = json.loads(resp.text).get(endpoint_child_key[0])
        for child in children:
            config_id = child.get(endpoint_child_key[1])
            resp = get_config_endpoint(f'{endpoint}/{config_id}')
            # print(resp.text)
            save_config(endpoint, f'{config_id}.json', resp.text, config_list)
    else:
        save_config(endpoint, 'root.json', resp.text, config_list)


def process_complex_endpoint(endpoint, paths, config_list):
    if endpoint == '/conditionalNaming/{type}':
        original_endpoint = copy.deepcopy(endpoint)
        conditional_naming_type_list = paths.get(endpoint).get('get').get('parameters')[0].get('schema').get('enum')
        for conditional_naming_type in conditional_naming_type_list:
            endpoint = original_endpoint.replace('{type}', conditional_naming_type)
            process_simple_endpoint(endpoint, ['values', 'id'], config_list)
    else:
        if endpoint == '/service/customServices/{technology}':
            original_endpoint = copy.deepcopy(endpoint)
            custom_service_technology_list = paths.get(endpoint).get('get').get('parameters')[0].get('schema').get('enum')
            for custom_service_technology in custom_service_technology_list:
                endpoint = original_endpoint.replace('{technology}', custom_service_technology)
                process_simple_endpoint(endpoint, ['values', 'id'], config_list)
        else:
            if endpoint in ['/applications/web/{id}/dataPrivacy', '/applications/web/{id}/errorRules', '/applications/web/{id}/keyUserActions']:
                original_endpoint = copy.deepcopy(endpoint)
                web_application_list = json.loads(get_config_endpoint('/applications/web').text).get('values')
                for web_application in web_application_list:
                    endpoint = original_endpoint.replace('{id}', web_application.get('id'))
                    process_simple_endpoint(endpoint, None, config_list)
            else:
                if endpoint in ['/applications/mobile/{applicationId}/keyUserActions', '/applications/mobile/{applicationId}/userActionAndSessionProperties']:
                    original_endpoint = copy.deepcopy(endpoint)
                    mobile_application_list = json.loads(get_config_endpoint('/applications/mobile').text).get('values')
                    for mobile_application in mobile_application_list:
                        endpoint = original_endpoint.replace('{applicationId}', mobile_application.get('id'))
                        process_simple_endpoint(endpoint, None, config_list)
                else:
                    if endpoint in ['/aws/credentials/{id}/services']:
                        original_endpoint = copy.deepcopy(endpoint)
                        aws_service_list = json.loads(get_config_endpoint('/aws/credentials').text)
                        for aws_service in aws_service_list:
                            endpoint = original_endpoint.replace('{id}', aws_service.get('id'))
                            process_simple_endpoint(endpoint, None, config_list)
                    else:
                        if endpoint in ['/azure/credentials/{id}/services']:
                            original_endpoint = copy.deepcopy(endpoint)
                            azure_service_list = json.loads(get_config_endpoint('/azure/credentials').text).get('values')
                            for azure_service in azure_service_list:
                                endpoint = original_endpoint.replace('{id}', azure_service.get('id'))
                                process_simple_endpoint(endpoint, None, config_list)


def save_config(endpoint, json_file_name, payload, config_list):
    # print(f'save_config({endpoint}, {json_file_name}, {payload})')
    directory_path = backup_directory_path + '/api/config/v1' + endpoint

    json_payload = json.loads(payload)
    # Fix id's based on entity_type and certain dynatrace created id's that contain "." characters
    if '/' in json_file_name or '.' in json_file_name:
        json_file_name = json_file_name.replace('/', '_')
        json_file_name = json_file_name.replace('.', '_')
        json_file_name = json_file_name.replace(':', '_')
        # some file names with these patterns are too long...
        json_file_name = json_file_name.replace('_json', '')
        json_file_name = json_file_name.replace('dynatrace_jmx_', '')
        json_file_name = json_file_name.replace('kafka_kafka', 'kafka')

    # Avoid duplicate names for entities that need subdirectories
    if 'APPLICATION' in json_file_name or 'AWS_CREDENTIALS' in json_file_name:
        json_file_name = f'{json_file_name}.json'

    write_json(directory_path, json_file_name, json_payload)

    json_payload['api-endpoint'] = endpoint
    config_list.append(json_payload)


def get_config_endpoint(endpoint):
    full_endpoint = f'/api/config/v1{endpoint}'
    return dynatrace_api.get_object_list(env, token, full_endpoint)


def save_settings20_objects():
    # print('save_settings20_objects()')
    filename = backup_directory_path + '/' + settings20_yaml_file_name
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}

    yaml_dict = copy.deepcopy(main_template)
    config_list = []

    exclude_schemas = ['']
    # include_schemas = ['builtin:logmonitoring.log-dpp-rules', 'builtin:logmonitoring.schemaless-log-metric', 'builtin:logmonitoring.log-custom-attributes']

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = dynatrace_api.get(env, token, endpoint, params)

    schema_ids = []
    schema_dict = {}

    for settings_json in settings_json_list:
        inner_settings_json_list = settings_json.get('items')
        for inner_settings_json in inner_settings_json_list:
            schema_id = inner_settings_json.get('schemaId')
            schema_ids.append(schema_id)
            latest_schema_version = inner_settings_json.get('latestSchemaVersion')
            schema_dict[schema_id] = latest_schema_version

    for schema_id in sorted(schema_ids):
        global long_file_suffix
        long_file_suffix = 0

        # if schema_id in include_schemas:
        if schema_id not in exclude_schemas:
            # display_name = inner_settings_json.get('displayName')
            # print(schema_id + ': ' + display_name)
            endpoint = '/api/v2/settings/objects'
            # raw_params = f'schemaIds={schema_id}&scopes=environment&fields=objectId,value&pageSize=500'
            raw_params = f'schemaIds={schema_id}&fields=objectId,value,scope&pageSize=500'
            params = urllib.parse.quote(raw_params, safe='/,&=')
            setting_object = dynatrace_api.get(env, token, endpoint, params)[0]
            items = setting_object.get('items')
            for item in items:
                # print(item)
                if schema_id == 'builtin:logmonitoring.log-dpp-rules' and '[Built-in]' in item.get('value').get('ruleName', ''):
                    pass
                    # print('Skipping ' + schema_id + ' rule ' + item.get('value').get('ruleName', ''))
                else:
                    # item['scope'] = 'environment'
                    item['schemaId'] = schema_id
                    item['schemaVersion'] = schema_dict[schema_id]
                    config_list.append(item)

                    write_settings20_json(schema_id, item)

    yaml_dict['configs'] = config_list

    with open(filename, 'w') as file:
        yaml.dump(yaml_dict, file, sort_keys=False)


def write_settings20_json(schema_id, json_dict):
    object_id = json_dict.get('objectId')
    # print(f'write_settings20_json({schema_id}, {str(json_dict)})')
    print(f'write_settings20_json({schema_id}, {str(object_id)})')
    dir_name = schema_id.replace(':', '.')
    save_path = backup_directory_path + '/api/v2/settings/objects/' + dir_name
    if object_id:
        write_json(save_path, object_id, json_dict)
    else:
        write_json(save_path, 'entity', json_dict)


def write_json(directory_path, filename, json_dict):
    # print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
    # print('write_json(' + directory_path + ',' + filename + ')')
    # print(directory_path)
    # print(filename)
    # print(json_dict)
    global long_file_suffix
    file_path = directory_path + '/' + filename
    if len(file_path) > 255:
        long_file_suffix += 1
        file_path = directory_path + '/' + str(long_file_suffix)
    if not os.path.isdir(directory_path):
        make_directory(directory_path)
    with open(file_path, 'w') as file:
        file.write(json.dumps(json_dict, indent=4, sort_keys=False))


def save_environment_objects():
    # print('save_environment_objects()')
    save_slo_objects()
    save_synthetic_monitor_objects()
    save_synthetic_location_objects()


def save_slo_objects():
    # print('save_slo_objects()')
    filename = backup_directory_path + '/' + environment_yaml_file_name
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}

    yaml_dict = copy.deepcopy(main_template)
    config_list = []

    endpoint = '/api/v2/slo'
    params = f'&pageSize=500'
    slo_json_list = dynatrace_api.get(env, token, endpoint, params)

    # print(slo_json_list)

    # Not needed
    # write_environment_json('api/v2/slo', 'root.json', slo_json_list)

    for slo_json in slo_json_list:
        inner_slo_json_list = slo_json.get('slo')
        for inner_slo_json in inner_slo_json_list:
            slo_id = inner_slo_json.get('id')
            write_environment_json('api/v2/slo', slo_id, inner_slo_json)
            config_list.append(inner_slo_json)

    yaml_dict['slos'] = config_list

    with open(filename, 'w') as file:
        yaml.dump(yaml_dict, file, sort_keys=False)


def save_synthetic_monitor_objects():
    # print('save_synthetic_monitor_objects()')
    filename = backup_directory_path + '/' + environment_yaml_file_name
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}

    yaml_dict = copy.deepcopy(main_template)
    config_list = []

    endpoint = '/api/v1/synthetic/monitors'
    raw_params = f'&pageSize=5000'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    synthetic_monitor_json_list = dynatrace_api.get(env, token, endpoint, params)

    # print(synthetic_monitor_json_list)

    # Not needed
    # write_environment_json('api/v1/synthetic/monitors', 'root.json', synthetic_monitor_json_list)

    for synthetic_monitor_json in synthetic_monitor_json_list:
        inner_synthetic_monitor_json_list = synthetic_monitor_json.get('monitors')
        for inner_synthetic_monitor_json in inner_synthetic_monitor_json_list:
            synthetic_monitor_id = inner_synthetic_monitor_json.get('entityId')
            endpoint = f'/api/v1/synthetic/monitors/{synthetic_monitor_id}'
            params = ''
            synthetic_monitor_details_json = dynatrace_api.get(env, token, endpoint, params)
            write_environment_json('api/v1/synthetic/monitors', synthetic_monitor_id, synthetic_monitor_details_json)
            config_list.append(inner_synthetic_monitor_json)

    yaml_dict['synthetic_monitors'] = config_list

    with open(filename, 'w') as file:
        yaml.dump(yaml_dict, file, sort_keys=False)


def save_synthetic_location_objects():
    # print('save_synthetic_location_objects()')
    filename = backup_directory_path + '/' + environment_yaml_file_name
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}

    yaml_dict = copy.deepcopy(main_template)
    config_list = []

    endpoint = '/api/v1/synthetic/locations'
    raw_params = f'&pageSize=5000'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    synthetic_location_json_list = dynatrace_api.get(env, token, endpoint, params)

    # print(synthetic_location_json_list)

    # Not needed
    # write_environment_json('api/v1/synthetic/location', 'root.json', synthetic_location_json_list)

    for synthetic_location_json in synthetic_location_json_list:
        inner_synthetic_location_json_list = synthetic_location_json.get('locations')
        for inner_synthetic_location_json in inner_synthetic_location_json_list:
            synthetic_location_id = inner_synthetic_location_json.get('entityId')
            endpoint = f'/api/v1/synthetic/locations/{synthetic_location_id}'
            params = ''
            synthetic_location_details_json = dynatrace_api.get(env, token, endpoint, params)
            write_environment_json('api/v1/synthetic/location', synthetic_location_id, synthetic_location_details_json)
            config_list.append(inner_synthetic_location_json)

    yaml_dict['synthetic_locations'] = config_list

    with open(filename, 'w') as file:
        yaml.dump(yaml_dict, file, sort_keys=False)


def write_environment_json(dir_name, environment_id, json_dict):
    # print(f'write_environment_json({dir_name}, {environment_id}, {json_dict})')
    print(f'write_environment_json({environment_id})')
    save_path = f'{backup_directory_path}/{dir_name}'
    write_json(save_path, environment_id, json_dict)


def confirm(message):
    # print('confirm(' + message + ')')
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_line_number())


def get_line_number():
    # print('get_line_number()')
    cf = currentframe()
    return cf.f_back.f_lineno


if __name__ == '__main__':
    confirm('Save settings for ' + env_name + '?')
    initialize()
    save_configuration_api_settings()
    save_settings20_objects()
    save_environment_objects()
