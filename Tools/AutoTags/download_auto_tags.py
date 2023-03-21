"""
Download auto tags from the tenant to the path indicated below.
"""
import json
import os
import re

from Reuse import dynatrace_api
from Reuse import environment


path_prefix = 'downloads'


def run():
    # pass
    download_auto_tags('Dev')


def save_auto_tag(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % json.dumps(content, indent=4))


def download_auto_tags(env_name):
    path = f'{path_prefix}/{env_name}'
    print(f'Downloading auto_tags for {env_name} to {path}')

    _, env, token = environment.get_environment(env_name)

    download_count = 0
    endpoint = '/api/config/v1/autoTags'
    res = json.loads(dynatrace_api.get_object_list(env,token, endpoint).text)

    for entry in res['values']:
        auto_tag_name = entry.get('name')
        auto_tag_id = entry.get('id')
        auto_tag = dynatrace_api.get_by_object_id(env, token, endpoint, auto_tag_id)
        clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{auto_tag_name}.json')
        print(f'Saving {auto_tag_name} ({auto_tag_id}) to {clean_filename}')
        save_auto_tag(path, clean_filename, auto_tag)
        download_count += 1

    print(f'Downloaded {download_count} auto_tags to {path}')


if __name__ == '__main__':
    run()
