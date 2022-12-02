import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    endpoint = '/api/config/v1/hosts/autoupdate'
    params = ''
    hosts_autoupdate_json = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]

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
    env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    # env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    process(env, token, True)


if __name__ == '__main__':
    # print('Not to be run standalone.  Use one of the "perform_*.py" modules to run this module.')
    # exit(1)
    main()
