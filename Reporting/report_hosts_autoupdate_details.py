from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/hosts/autoupdate'
    params = ''
    hosts_autoupdate_json = dynatrace_api.get(env, token, endpoint, params)[0]

    if print_mode:
        print('setting' + '|' + 'version' + '|' + 'updateWindows')

    setting = hosts_autoupdate_json.get('setting')
    version = hosts_autoupdate_json.get('version')
    update_windows = hosts_autoupdate_json.get('updateWindows').get("windows")

    # TESTING
    # setting = DISABLED
    # version = "1.x"
    # updateWindows = ['fake']

    if print_mode:
        print(str(setting) + '|' + str(version) + '|' + str(update_windows))

    if setting == 'ENABLED' and version is None and update_windows == []:
        summary.append('OneAgent Auto Update is turned on.  This is not recommended for Production environments.  Consider doing manual updates or using OneAgent Maintenance Windows.')
    else:
        summary.append('OneAgent Auto Update settings have been modified as follows.' + '\r\n' +
                       'Setting is ' + setting + ', version is ' + str(version) + ' and update windows are ' + str(update_windows) + '.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def convert_boolean(boolean):
    if boolean:
        return 'on'
    else:
        return'off'


def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
