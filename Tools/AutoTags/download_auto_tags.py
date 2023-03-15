"""
Download auto tags from the tenant to the path indicated below.
"""
import json
import os
import re
import requests
import ssl

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
    try:
        headers = {'Authorization': 'Api-Token ' + token}
        r = requests.get(env + '/api/config/v1/autoTags', headers=headers)
        res = r.json()
        for entry in res['values']:
            auto_tag_name = entry.get('name')
            auto_tag_id = entry.get('id')
            # auto_tag_description = entry.get('description')
            response = requests.get(env + '/api/config/v1/autoTags/' + auto_tag_id, headers=headers)
            auto_tag = response.json()
            clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{auto_tag_name}.json')
            print(f'Saving {auto_tag_name} ({auto_tag_id}) to {clean_filename}')
            save_auto_tag(path, clean_filename, auto_tag)
            download_count += 1
        print(f'Downloaded {download_count} auto_tags to {path}')
    except ssl.SSLError:
        print("SSL Error")


if __name__ == '__main__':
    run()
