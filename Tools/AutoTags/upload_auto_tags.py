# POST auto tags matching the file path pattern to the specified environment.

import json
import glob
import requests
import ssl
import codecs

from Reuse import environment


def run():
    # pass
    upload_auto_tags('Dev', 'uploads/DEV/*.json')


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
    url = env + '/api/config/v1/autoTags/'
    print('post: ' + url)
    try:
        r = requests.post(url, payload.encode('utf-8'), headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
        # If you need to bypass certificate checks on managed and are ok with the risk:
        # r = requests.post(url, payload, headers=HEADERS, verify=False)
        if r.status_code not in [200, 201, 204]:
            print('Status Code: %d' % r.status_code)
            print('Reason: %s' % r.reason)
            if len(r.text) > 0:
                print(r.text)
    except ssl.SSLError:
        print('SSL Error')


if __name__ == '__main__':
    run()
