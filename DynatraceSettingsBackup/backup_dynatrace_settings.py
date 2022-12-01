"""
Save Dynatrace settings to a single YAML file that can be used to PUT, POST, or DELETE settings later, and to JSON files.

Specifically Covers:
All Settings 2.0 configurations, based on a full list of schemas returned by the API.
Settings in the Configuration API spec (which must be downloaded manually and saved as "config_v1_spec3.json").

Token Permissions Required:
"Read configuration: ReadConfig"
"Read settings: settings.read"
"credentialVault.read (Read credential vault entries)" - if you want to save credentials
"DssFileManagement (Mobile symbolication file management)" - if you want to save symbol files

"""
import copy
from inspect import currentframe
import json
import os
import requests
import shutil
import ssl
import yaml

# Environment Details (Short Name, Tenant, Token)
# environment_details = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# environment_details = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
environment_details = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')

env_name = environment_details[0]
tenant = os.environ.get(environment_details[1])
token = os.environ.get(environment_details[2])
env = f'https://{tenant}.live.dynatrace.com'

backup_directory_path = '../$Output/Backup_' + env_name

settings20_yaml_file_name = 'settings20.yaml'
config_yaml_file_name = 'config.yaml'
confirmation_required = True
long_file_suffix = 0

# Set to False for partial runs (configs only, settings only)
remove_directory_at_startup = True

configs = []

child_endpoints_covered_by_lists = []
child_endpoints_not_covered_by_lists = []

extensions_technology_list = []


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + backup_directory_path + ' directory will now be removed to prepare for backup.')
        remove_directory(backup_directory_path)

    if not os.path.isdir(backup_directory_path):
        make_directory(backup_directory_path)


def remove_directory(path):
    print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


# def makedir(path):
#     print('makedir(' + path + ')')
#
#     try:
#         os.mkdir(path)
#     except OSError:
#         print('Creation of the directory %s failed' % path)
#         exit()
#     else:
#         print('Successfully created the directory %s ' % path)
#
#
def save_entity(entity_type):
    print('save_entity(' + entity_type + ')')

    if '/binary' in entity_type:
        print('Skipping binary entity!')
        return
    try:
        full_url = env + '/api/config/v1' + entity_type
        resp = requests.get(full_url, headers={'Authorization': 'Api-Token ' + token})
        if resp.status_code != 200:
            print('REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            print(resp.text)
        else:
            save(entity_type, resp.json())
    except ssl.SSLError:
        print('SSL Error')
        exit(get_linenumber())


def save_list(list_type):
    print('save_list(' + list_type + ')')
    try:
        full_url = env + '/api/config/v1' + list_type
        resp = requests.get(full_url, headers={'Authorization': 'Api-Token ' + token})

        if resp.status_code != 200:
            print('REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            print(resp.text)
        else:
            resp_json = resp.json()
            inner_key = 'values'
            if list_type == '/extensions':
                inner_key = 'extensions'
            else:
                if list_type == '/dashboards':
                    inner_key = 'dashboards'
                else:
                    if list_type == '/credentials':
                        inner_key = 'credentials'
                    else:
                        if list_type == '/symfiles':
                            inner_key = 'symbolFiles'
            if resp_json and 'Old API endpoints are disabled' not in str(resp_json):
                if list_type == '/aws/credentials':
                    entries = resp_json
                else:
                    entries = resp_json[inner_key]

                if entries:
                    for entry in entries:
                        if list_type == '/applications/web/dataPrivacy':
                            entity_id = entry['identifier']
                            full_url = env + '/api/config/v1/applications/web/' + entity_id + '/dataPrivacy'
                        else:
                            entity_id = entry['id']
                            full_url = env + '/api/config/v1' + list_type + '/' + entity_id
                        resp = requests.get(full_url, headers={'Authorization': 'Api-Token ' + token})
                        if resp.status_code != 200:
                            print('REST API Call Failed!')
                            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
                            print(resp.text)
                        else:
                            save(list_type, resp.json())
    except ssl.SSLError:
        print('SSL Error')
        exit(get_linenumber())


def get_rest_api_json(endpoint, params):
    print('get_rest_api_json(' + env + ', ' + token + ', ' + endpoint + ', ' + params + ')')
    full_url = env + endpoint
    resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})
    if resp.status_code != 200 and resp.status_code != 404:
        print('REST API Call Failed!')
        print(f'GET {full_url} {params} {resp.status_code} - {resp.reason}')
        print(resp.text)
        exit(get_linenumber())

    json_data = resp.json()

    # Some json is just a list of dictionaries.
    # Config V1 AWS Credentials is the only example I am aware of.
    # For these, I have never seen pagination.
    if type(json_data) is list:
        return json_data

    json_list = [json_data]
    next_page_key = json_data.get('nextPageKey')

    while next_page_key is not None:
        params = {'nextPageKey': next_page_key}
        # full_url = env + endpoint
        resp = requests.get(full_url, params=params, headers={'Authorization': "Api-Token " + token})

        if resp.status_code != 200:
            print('Paginated REST API Call Failed!')
            print(f'GET {full_url} {resp.status_code} - {resp.reason}')
            print(resp.text)
            exit(get_linenumber())

        json_data = resp.json()

        next_page_key = json_data.get('nextPageKey')
        json_list.append(json_data)

    return json_list


def save_configuration_api_settings():
    print('save_configuration_api_settings()')

    global extensions_technology_list

    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    extensions_technology_list = paths.get('/extensions/{technology}/availableHosts').get('get').get('parameters')[0].get('schema').get('enum')
    # print(extensions_technology_list)

    endpoint_methods = {}

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        # print(endpoint)
        endpoint_dict = paths.get(endpoint)
        methods = list(endpoint_dict.keys())
        endpoint_methods[endpoint] = methods

    for endpoint in endpoints:
        load_child_endpoints(endpoint, endpoint_methods, paths)

    # print(child_endpoints_covered_by_lists)
    # print(child_endpoints_not_covered_by_lists)
    # exit(get_linenumber())

    for endpoint in endpoints:
        if process_endpoint(endpoint):
            supported_methods = endpoint_methods.get(endpoint)
            if 'get' in supported_methods:
                endpoint_dict = paths.get(endpoint)
                get_dict = endpoint_dict.get('get')
                summary = get_dict.get('summary')
                responses_dict = get_dict.get('responses')
                response_200_dict = responses_dict.get('200')
                response_200_content = response_200_dict.get('content')
                if summary.startswith('Lists') and ('List' in str(response_200_content) or 'EntityShortRepresentation' in str(response_200_content)):
                    save_list(endpoint)
                else:
                    save_entity(endpoint)

    # If you want to select some entities you can comment out the logic above and uncomment the ones you want below.
    # save_entity("/allowedBeaconOriginsForCors")
    # save_entity("/anomalyDetection/applications")
    # save_entity("/anomalyDetection/aws")
    # save_entity("/anomalyDetection/databaseServices")
    # save_entity("/anomalyDetection/hosts")
    # save_entity("/anomalyDetection/services")
    # save_entity("/anomalyDetection/vmware")
    # save_entity("/applicationDetectionRules/hostDetection")
    # save_entity("/applications/web/default")
    # save_entity("/applications/web/default/dataPrivacy")
    # save_entity("/aws/iamExternalId")
    # save_entity("/aws/privateLink")
    # save_entity("/aws/privateLink/allowlistedAccounts")
    # save_entity("/aws/supportedServices")
    # save_entity("/azure/supportedServices")
    # save_entity("/contentResources")
    # save_entity("/frequentIssueDetection")
    # save_entity("/geographicRegions/ipAddressMappings")
    # save_entity("/geographicRegions/ipDetectionHeaders")
    # save_entity("/hosts/autoupdate")
    # save_entity("/symfiles/dtxdss-download")
    # save_entity("/symfiles/info")
    # save_entity("/symfiles/ios/supportedversion")
    # save_entity("/technologies")
    #
    # save_list("/alertingProfiles")
    # save_list("/anomalyDetection/diskEvents")
    # save_list("/anomalyDetection/metricEvents")
    # save_list("/applicationDetectionRules")
    # save_list("/applications/mobile")
    # save_list("/applications/web")
    # save_list("/applications/web/dataPrivacy")
    # save_list("/autoTags")
    # save_list("/aws/credentials")
    # save_list("/azure/credentials")
    # save_list("/calculatedMetrics/mobile")
    # save_list("/calculatedMetrics/rum")
    # save_list("/calculatedMetrics/service")
    # save_list("/calculatedMetrics/synthetic")
    # save_list("/cloudFoundry/credentials")
    # save_list("/credentials")
    # save_list("/dashboards")
    # # "/dataPrivacy" does not actually return a list
    # save_entity("/dataPrivacy")
    # save_list("/extensions")
    # save_list("/extensions/activeGateExtensionModules")
    # save_list("/kubernetes/credentials")
    # save_list("/maintenanceWindows")
    # save_list("/managementZones")
    # save_list("/notifications")
    # save_list("/plugins")
    # save_list("/plugins/activeGatePluginModules")
    # save_list("/remoteEnvironments")
    # save_list("/reports")
    # save_list("/service/detectionRules/FULL_WEB_REQUEST")
    # save_list("/service/detectionRules/FULL_WEB_SERVICE")
    # save_list("/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_REQUEST")
    # save_list("/service/detectionRules/OPAQUE_AND_EXTERNAL_WEB_SERVICE")
    # save_list("/service/failureDetection/parameterSelection/parameterSets")
    # save_list("/service/failureDetection/parameterSelection/rules")
    # save_list("/symfiles")
    # # "/service/resourceNaming" does not actually return a list
    # save_entity("/service/resourceNaming")
    #
    # These have problems due to missing permissions or other issues.
    # # save_list("/calculatedMetrics/log")
    # # save_list("/service/ibmMQTracing/imsEntryQueue")
    # # save_list("/service/ibmMQTracing/queueManager")

    filename = backup_directory_path + '/' + config_yaml_file_name
    write_yaml(filename)


def load_child_endpoints(endpoint, endpoint_methods, paths):
    print('load_child_endpoints(' + endpoint + ', ' + str(endpoint_methods) + ', ' + str(paths) + ')')
    global child_endpoints_covered_by_lists
    global child_endpoints_not_covered_by_lists

    # if process_endpoint(endpoint):
    supported_methods = endpoint_methods.get(endpoint)
    debug = False
    # if '/calculatedMetrics/' in endpoint:
    # if endpoint in ['/alertingProfiles']:
    # 	debug = True
    if debug:
        print('DEBUG')
        print(endpoint)
        print(supported_methods)
    if 'get' in supported_methods:
        endpoint_dict = paths.get(endpoint)
        get_dict = endpoint_dict.get('get')
        summary = get_dict.get('summary')
        if debug:
            print(summary)
        responses_dict = get_dict.get('responses')
        response_200_dict = responses_dict.get('200')
        response_200_content = response_200_dict.get('content')
        if debug:
            print(response_200_content)
        if summary.startswith('List') and ('List' in str(response_200_content) or 'EntityShortRepresentation' in str(response_200_content)):
            if endpoint.startswith('/calculatedMetrics/'):
                child_endpoints_covered_by_lists.append(endpoint + '/{metricKey}')
            else:
                child_endpoints_covered_by_lists.append(endpoint + '/{id}')
    # else:
    # 	return

    if '/validator' in endpoint:
        return
    if '{' not in endpoint:
        return
    if endpoint in child_endpoints_covered_by_lists:
        return
    if endpoint.startswith('/aws/privateLink'):
        return

    # print('Child Endpoint Loaded to the "Child Enpoints Not Covered by Lists" list: ' + endpoint)
    child_endpoints_not_covered_by_lists.append(endpoint)


def process_endpoint(endpoint):
    print('process_endpoint(' + endpoint + ')')
    # /calculatedMetrics/log is obsolete if new logging is used (400 - Bad Request)
    # /service/ibmMQTracing/imsEntryQueue is obsolete (410 - Gone)
    # /service/ibmMQTracing/queueManager is obsolete (410 - Gone)
    problematic_endpoints = [
        '/calculatedMetrics/log',
        '/service/ibmMQTracing/imsEntryQueue',
        '/service/ibmMQTracing/queueManager'
    ]

    # To focus only on specific endpoints when testing...
    # test_endpoints = ['/aws/credentials', '/anomalyDetection/aws']
    # if endpoint in test_endpoints:
    # 	return True
    # else:
    # 	return False

    # To focus only on the problematic endpoints when testing...
    # if endpoint in problematic_endpoints:
    # 	return True
    # else:
    # 	return False

    # To skip these...
    # no_permissions_yet = ['/credentials', '/symfiles', '/symfiles/dtxdss-download', '/symfiles/info', '/symfiles/ios/supportedversion']
    # problematic_endpoints.extend(no_permissions_yet)

    # To skip these for testing
    skip_for_speed_when_testing = ['/dashboards', '/extensions', '/anomalyDetection/metricEvents', '/calculatedMetrics/service', '/service/requestAttributes']
    problematic_endpoints.extend(skip_for_speed_when_testing)

    # Do this only when you want to "fast-forward" past a problematic one!
    # if endpoint <= '/service/ibmMQTracing/queueManager/{name}':
    # 	print('Skipping ' + endpoint + ' to fast-forward past the prior problematic endpoint')
    # 	return False
    # if endpoint < '/aws/privateLink/allowlistedAccounts':
    #     print('Skipping ' + endpoint + ' to fast-forward to a specific endpoint')
    #     return False
    # if endpoint > '/applications/web/z':
    # 	print('Skipping ' + endpoint + ' to fast-forward past a specific endpoint')
    # 	return False

    if '/validator' in endpoint:
        # print('Skipping ' + endpoint + ' because it is a validator')
        return False
    if '{' in endpoint:
        # print('Skipping ' + endpoint + ' because it contains a brace character ("{")')
        return False
    if endpoint in problematic_endpoints:
        # print('Skipping ' + endpoint + ' because it is in the problematic endpoint list')
        return False

    return True


def save(entity_type, yaml_dict):
    print('save(' + entity_type + ',' + str(yaml_dict))
    # Some entity types (like '/aws/credentials') may contain an empty string
    if isinstance(yaml_dict, dict):
        yaml_dict['endpoint'] = entity_type
    else:
        # print('Wrapping ' + entity_type + ' in a dictionary')
        # print('Input Content: ' + str(yaml_dict))
        # print('Input Type: ' + str(type(yaml_dict)))
        new_yaml_dict = {'value': yaml_dict, 'endpoint': entity_type}
        yaml_dict = new_yaml_dict
        # print('Output Content: ' + str(yaml_dict))
    global configs
    configs.append(yaml_dict)

    # The 'endpoint' field is needed for single-file YAML, but not for JSON files
    yaml_dict.pop('endpoint')
    write_configuration_api_json(entity_type, yaml_dict)

    if has_children(entity_type):
        # print(entity_type + ' has children!')
        for _ in get_child_endpoints(entity_type):
            save_child_endpoints(entity_type, yaml_dict)


def has_children(entity_type):
    print('has_children(' + entity_type + ')')
    for endpoint in child_endpoints_not_covered_by_lists:
        if endpoint.startswith(entity_type):
            return True
    return False


def get_child_endpoints(entity_type):
    print('get_child_endpoints(' + entity_type + ')')
    endpoints = []
    for endpoint in child_endpoints_not_covered_by_lists:
        if endpoint.startswith(entity_type):
            endpoints.append(endpoint)
    return endpoints


def save_child_endpoints(parent_entity_type, parent_yaml_dict):
    print('save_child_endpoints(' + parent_entity_type + ', ' + str(parent_yaml_dict) + ')')
    endpoint = ''
    for child_endpoint in get_child_endpoints(parent_entity_type):
        # performance_skip_list = ['/extensions/{technology}/availableHosts', '/extensions/{id}/instances/{configurationId}']
        # if child_endpoint in performance_skip_list:
        if child_endpoint.startswith('/extensions'):
            print('Skipping ' + child_endpoint + ' for performance reasons')
        else:
            # print('Child endpoint (incoming): ' + child_endpoint)
            if child_endpoint.startswith('/applications/web/') or child_endpoint.startswith('/applications/mobile/'):
                id_key = 'identifier'
            else:
                if child_endpoint.startswith('/aws/privateLink/allowlistedAccounts/'):
                    id_key = 'endpoint'
                else:
                    id_key = 'id'
            parent_id = parent_yaml_dict.get(id_key)
            if not parent_id:
                print('id not found for parent_entity_type: ' + parent_entity_type)
                print('id_key: ' + id_key)
                print('parent_yaml_dict: ' + str(parent_yaml_dict))
                exit(get_linenumber())
            if child_endpoint == '/extensions/{technology}/availableHosts':
                for extensions_technology in extensions_technology_list:
                    endpoint = child_endpoint.replace('{technology}', extensions_technology)
                    # print('Child endpoint (outgoing): ' + endpoint)
            else:
                endpoint = child_endpoint.replace('{id}', parent_id)
                # print('Child endpoint (outgoing): ' + endpoint)

        save_entity(endpoint)


def write_yaml(filename):
    print('write_yaml(' + filename + ')')
    global configs
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}
    yaml_dict = copy.deepcopy(main_template)
    yaml_dict['configs'] = configs

    with open(filename, 'w') as file:
        yaml.dump(yaml_dict, file, sort_keys=False)


def write_configuration_api_json(entity_type, json_dict):
    print('write_configuration_api_json(' + entity_type + ',' + str(json_dict) + ')')
    directory_path = backup_directory_path + '/api/config/v1' + entity_type + '/'

    if entity_type.startswith('/applications/web/') or entity_type.startswith('/applications/mobile/'):
        id_key = 'identifier'
    else:
        if entity_type.startswith('/aws/privateLink/allowlistedAccounts/'):
            id_key = 'endpoint'
        else:
            id_key = 'id'

    config_id = json_dict.get(id_key)

    if not config_id:
        config_id = entity_type

    # Fix id's based on entity_type and certain dynatrace created id's that contain "." characters
    if '/' in config_id or '.' in config_id:
        config_id = config_id[1:].replace('/', '_')
        config_id = config_id.replace('.', '_')

    # if entity_type.startswith('/extensions'):
    #     print('Skipping ' + entity_type + ' for performance reasons')
    #     return

    write_json(directory_path, config_id, json_dict)


def save_settings20_objects():
    print('save_settings20_objects()')
    filename = backup_directory_path + '/' + settings20_yaml_file_name
    main_template = {'tenant': env_name, 'action': 'validate', 'configs': []}

    yaml_dict = copy.deepcopy(main_template)
    config_list = []

    exclude_schemas = ['']
    # include_schemas = ['builtin:logmonitoring.log-dpp-rules', 'builtin:logmonitoring.schemaless-log-metric', 'builtin:logmonitoring.log-custom-attributes']

    endpoint = '/api/v2/settings/schemas'
    params = ''
    settings_json_list = get_rest_api_json(endpoint, params)

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
            # params = 'schemaIds=' + schema_id.replace(':', '%3A') + '&scopes=environment&fields=objectId%2Cvalue&pageSize=500'
            params = 'schemaIds=' + schema_id.replace(':', '%3A') + '&fields=objectId%2Cvalue%2Cscope&pageSize=500'
            setting_object = get_rest_api_json(endpoint, params)[0]
            items = setting_object.get('items')
            for item in items:
                print(item)
                if schema_id == 'builtin:logmonitoring.log-dpp-rules' and '[Built-in]' in item.get('value').get('ruleName', ''):
                    print('Skipping ' + schema_id + ' rule ' + item.get('value').get('ruleName', ''))
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
    print('write_settings20_json(' + schema_id + ',' + str(json_dict) + ')')
    dir_name = schema_id.replace(':', '.')
    save_path = backup_directory_path + '/api/v2/settings/objects/' + dir_name

    object_id = json_dict.get('objectId')
    if object_id:
        write_json(save_path, object_id, json_dict)
    else:
        write_json(save_path, 'entity', json_dict)


def write_json(directory_path, filename, json_dict):
    print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
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


def make_directory(path):
    print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    print('confirm(' + message + ')')
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_linenumber())


def get_linenumber():
    print('get_linenumber()')
    cf = currentframe()
    return cf.f_back.f_lineno


if __name__ == '__main__':
    confirm('Save settings for ' + env_name + '?')
    initialize()
    save_configuration_api_settings()
    save_settings20_objects()
