import os
import sys
import json

from Reuse import dynatrace_api
from Reuse import environment


selector_file_name = '../../$Input/Tools/Metrics/metrics.txt'
PATH = PATH = '../../$Output/Tools/Metrics/Saved'


def save(path, file, content):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + "/" + file, "w", encoding='utf8') as text_file:
        text_file.write("%s" % json.dumps(content, indent=4))


def save_metric(env, token, metric_id):
    metric = dynatrace_api.get_by_object_id(env, token, endpoint='/api/v2/metrics', object_id=metric_id)
    print('Saving ' + metric_id + ' to ' + PATH)
    save(PATH, metric_id.replace(':', '-') + '.json', metric)


def process(env, token):
    selector_file = open(selector_file_name, 'r')
    for line in selector_file:
        metric_id = line.rstrip()
        save_metric(env, token, metric_id)
    selector_file.close()

    print('Done!')


def run():
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

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
