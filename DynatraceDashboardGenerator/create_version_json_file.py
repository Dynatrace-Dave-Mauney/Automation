#
# Save version from Dynatrace REST API to a file.
#

import json
import sys

from Reuse import dynatrace_api

def get_version(url, token):
    endpoint = '/api/v1/config/clusterversion'
    params = ''
    json_list = dynatrace_api.get(url, token, endpoint, params)
    # version: str = json_list[0].get('version', '')
    version = json_list[0]
    return version


def write_version_file(url, token):
    version = get_version(url, token)
    with open('version.json', 'w') as file:
        file.write(json.dumps(version))
        print(f'version {version.get("version")} was written to {file.name}')


def process(arguments):
    # Assume tenant/environment URL followed by Token
    url = arguments[1]
    token = arguments[2]

    print('url: ' + url)
    print('token: ' + token[0:31] + '.*' + ' (masked for security)')

    write_version_file(url, token)


def main(arguments):
    help_text = '''
    create_version_file.py creates a version.txt file for an environment

    Usage:    create_version_file.py <tenant/environment URL> <token>
    '''

    print('args' + str(arguments))
    if len(arguments) < 2:
        print(help_text)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help_text)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help_text)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 3:
            process(arguments)
        else:
            print(help_text)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
