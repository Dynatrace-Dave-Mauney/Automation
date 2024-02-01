"""
Download various entities from the tenant to a specified directory.
"""

import json
import os
import re

from Reuse import dynatrace_api


def download(env_name, env, token, entity_type, endpoint, download_path, **kwargs):
    values_key = kwargs.get('values_key', 'values')
    name_key = kwargs.get('name_key', 'name')
    id_key = kwargs.get('id_key', 'id')
    path = download_path
    if env_name:
        path += f'/{env_name}'
    if entity_type:
        path += f'/{entity_type}'

    print(f'Downloading {entity_type} entities for {env_name} to {path}')

    download_count = 0
    r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
    entity_json = r.json()
    entity_values = entity_json.get(values_key)
    for entity_value in entity_values:
        entity_name = entity_value.get(name_key)
        entity_id = entity_value.get(id_key)
        r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{entity_id}', token)
        entity = r.json()
        clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{entity_name}.json')
        print(f'Saving {entity_name} ({entity_id}) to {clean_filename}')
        save_entity(path, clean_filename, entity)
        download_count += 1

    print(f'Downloaded {download_count} {entity_type} entities to {path}')


def save_entity(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % json.dumps(content, indent=4))
