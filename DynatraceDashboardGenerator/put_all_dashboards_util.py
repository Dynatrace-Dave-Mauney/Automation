# Put all dashboards in the current directory to tenant/environment specified via command line argument.
#
# CAUTION:
#
# The file name is assumed to be the dashboard id.
# All files in the current directory with the following format will be assumed to be dashboards:
# ????????-????-????-????-????????????.json
# Example:
# aaaaaaaa-bbbb-cccc-dddd-000000000001.json
#

import glob
import requests
import ssl
import sys


def put_dashboard(env, token, dashboard_id, payload):
    url = env + '/api/config/v1/dashboards/' + dashboard_id
    print('PUT: ' + url)
    try:
        r = requests.put(url, payload,
                         headers={'Authorization': 'Api-Token ' + token,
                                  'Content-Type': 'application/json; charset=utf-8'})
        # If you need to bypass certificate checks on managed and are ok with the risk:
        # r = requests.put(url, payload, headers=HEADERS, verify=False)
        print('Status Code: %d' % r.status_code)
        if len(r.text) > 0:
            print(r.text)
        if r.status_code not in [200, 204]:
            exit()
    except ssl.SSLError:
        print('SSL Error')


def put_dashboards(env, token):
    path = './????????-????-????-????-????????????.json'
    for filename in glob.glob(path):
        with open(filename, 'r') as f:
            dashboard_id = filename.replace('.json', '').replace('.\\', '')
            put_dashboard(env, token, dashboard_id, f.read())


def main(arguments):
    usage = '''
    put_all_dashboards.py: Put all dashboards in the current directory to tenant/environment 
    specified via command line argument.

    Usage:    put_all_dashboards.py <tenant/environment URL> <token>
    Examples: put_all_dashboards.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              put_all_dashboards.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
    '''

    print('args' + str(arguments))
    if len(arguments) < 2:
        print(usage)
        raise ValueError('Too few arguments!')
    if len(arguments) > 3:
        print(help)
        raise ValueError('Too many arguments!')
    if arguments[1] in ['-h', '--help']:
        print(help)
    elif arguments[1] in ['-v', '--version']:
        print('1.0')
    else:
        if len(arguments) == 3:
            put_dashboards(arguments[1], arguments[2])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
