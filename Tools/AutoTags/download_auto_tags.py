"""
Download auto tags from the tenant to the path indicated below.
"""
import json
import os
import re

from Reuse import dynatrace_api
from Reuse import environment


path_prefix = 'downloads'


def save_auto_tag(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % json.dumps(content, indent=4))


def process(env_name, env, token):
    path = f'{path_prefix}/{env_name}'
    print(f'Downloading auto_tags for {env_name} to {path}')

    download_count = 0
    endpoint = '/api/config/v1/autoTags'
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    auto_tag_json = json.loads(r.text)
    auto_tag_values = auto_tag_json.get('values')
    for auto_tag_value in auto_tag_values:
        auto_tag_name = auto_tag_value.get('name')
        auto_tag_id = auto_tag_value.get('id')
        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{auto_tag_id}', token)
        auto_tag = json.loads(r.text)
        clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{auto_tag_name}.json')
        print(f'Saving {auto_tag_name} ({auto_tag_id}) to {clean_filename}')
        save_auto_tag(path, clean_filename, auto_tag)
        download_count += 1

    print(f'Downloaded {download_count} auto_tags to {path}')


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env_name, env, token)


if __name__ == '__main__':
    main()
