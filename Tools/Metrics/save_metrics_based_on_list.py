import os
import requests
import ssl
import sys
import json
# from pathlib import Path

selector_file_name = '../../$Input/Tools/Metrics/metrics.txt'
PATH = PATH = '../../$Output/Tools/Metrics/Saved'


def save(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % json.dumps(content, indent=4))


def save_metric(metric, env, token):
    headers = {'Authorization': 'Api-Token ' + token}
    try:
        r = requests.get(env + '/api/v2/metrics/' + metric, headers=headers)
        print('Saving ' + metric + ' to ' + PATH)
        save(PATH, metric.replace(':', '-') + '.json', r.json())
    except ssl.SSLError:
        print("SSL Error")


def process(env, token):
    selector_file = open(selector_file_name, 'r')
    for line in selector_file:
        metric = line.rstrip()
        save_metric(metric, env, token)
    selector_file.close()

    print('Done!')


def run():
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token)


def main(arguments):
    usage = '''
    save_metrics_based_on_list.py: Save all metrics in the selector list 

    Usage:    save_metrics_based_on_list.py <tenant/environment URL> <token>
    Examples: save_metrics_based_on_list.py https://<TENANT>.live.dynatrace.com ABCD123ABCD123
              save_metrics_based_on_list.py https://<TENANT>.dynatrace-managed.com/e/<ENV>> ABCD123ABCD123
    '''

    # print('args' + str(arguments))
    if len(arguments) == 1:
        run()
        exit()
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
            process(arguments[1], arguments[2])
        else:
            print(usage)
            raise ValueError('Incorrect arguments!')


if __name__ == '__main__':
    main(sys.argv)
