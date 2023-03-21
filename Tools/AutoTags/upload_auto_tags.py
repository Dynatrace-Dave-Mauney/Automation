# POST auto tags matching the file path pattern to the specified environment.

import json
import glob
import codecs

from Reuse import dynatrace_api
from Reuse import environment


def run():
    # pass
    upload_auto_tags('Personal', 'uploads/DEV/*.json')


def upload_auto_tags(env_name, path):
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            auto_tag = f.read()
            auto_tag_json = json.loads(auto_tag)
            auto_tag_id = auto_tag_json.get('id')
            # Remove any id before POST
            if auto_tag_id:
                auto_tag_json.pop('id')
            auto_tag_name = auto_tag_json.get('name')
            print(filename + ': ' + auto_tag_id + ': ' + auto_tag_name)
            _, env, token = environment.get_environment(env_name)
            post_auto_tag(env, token, auto_tag_id, json.dumps(auto_tag_json))


def post_auto_tag(env, token, auto_tag_id, payload):
    endpoint = '/api/config/v1/autoTags'
    dynatrace_api.post(env, token, endpoint, payload)


if __name__ == '__main__':
    run()
