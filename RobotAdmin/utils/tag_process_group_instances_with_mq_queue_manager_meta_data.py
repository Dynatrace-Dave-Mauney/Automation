from inspect import currentframe
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


# Can be modified.  This is the key used for the tag.
tag_key = 'Queue Manager'

# Should remain constant.  This is the key for the plugin metadata used to identify MQ Queue Managers.
plugin_key = 'Queue manager'

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')


def process():
    entity_type = 'PROCESS_GROUP_INSTANCE'
    endpoint = '/api/v2/entities'
    entity_selector = 'type(' + entity_type + ')'
    params = '&entitySelector=' + urllib.parse.quote(entity_selector) + '&fields=' + urllib.parse.quote('properties.softwareTechnologies,properties.customPgMetadata,tags')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')
            properties = inner_entities_json.get('properties')
            software_technologies = properties.get('softwareTechnologies')
            custom_process_group_metadata = properties.get('customPgMetadata')
            if "IBM_MQ" in str(software_technologies) and \
                    plugin_key in str(custom_process_group_metadata) and \
                    'Queue Manager' not in str(inner_entities_json.get('tags')):
                for custom_process_group_metadata_item in custom_process_group_metadata:
                    if custom_process_group_metadata_item.get('key').get('key') == plugin_key:
                        queue_manager = custom_process_group_metadata_item.get('value')
                        print(f'Tagging {display_name} ({entity_id}) with {tag_key}: {queue_manager}')
                        post_queue_manager_tag(entity_id, queue_manager)


def post_queue_manager_tag(entity_id, queue_manager):
    entity_selector = 'entityId("' + entity_id + '")'
    params = '?entitySelector=' + urllib.parse.quote(entity_selector)
    endpoint = '/api/v2/tags' + params
    tag_body = '{"tags": [{"key": "' + tag_key + '", "value": "' + queue_manager + '"}]}'
    post(endpoint, tag_body)


def post(endpoint, payload):
    return dynatrace_api.post(env, token, endpoint, payload)


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


if __name__ == '__main__':
    process()
