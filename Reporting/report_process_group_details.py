import dynatrace_rest_api_helper
import os


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    counts_primary_icon_type = {}

    endpoint = '/api/v2/entities'
    params = 'pageSize=4000&entitySelector=type%28%22process_group%22%29&fields=%2Bproperties%2C%2Bicon&to=-5m'
    entities_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)
    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'detectedName' + '|' + 'metadata' + '|' + 'listenPorts' + '|' + 'primaryIconType')
    for entities_json in entities_json_list:
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            # DEBUG
            # print(inner_entities_json)
            # exit()
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            properties = inner_entities_json.get('properties')

            detected_name = properties.get('detectedName', '')
            metadata = str(properties.get('metadata', ''))
            metadata = metadata.replace("{", "")
            metadata = metadata.replace("}", "")
            metadata = metadata.replace("[", "")
            metadata = metadata.replace("]", "")
            metadata = metadata.replace(" 'value':", ":")
            metadata = metadata.replace("'key':", "")
            metadata = metadata.replace(" '", "")
            metadata = metadata.replace("',", "")
            metadata = metadata.replace("'", "")

            listen_ports = str(properties.get('listenPorts', ''))
            listen_ports = listen_ports.replace('[', '')
            listen_ports = listen_ports.replace(']', '')

            icon = inner_entities_json.get('icon')
            if icon:
                primary_icon_type = icon.get('primaryIconType')
            else:
                primary_icon_type = 'NONE'

            if print_mode:
                print(entity_id + '|' + display_name + '|' + detected_name + '|' + metadata + '|' + listen_ports + '|' + primary_icon_type)

            count_total += 1
            counts_primary_icon_type[primary_icon_type] = counts_primary_icon_type.get(primary_icon_type, 0) + 1

    counts_primary_icon_type_str = str(sorted(counts_primary_icon_type.items()))
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('[', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace(']', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('), (', '~COMMA~')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('(', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace(')', '')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace(',', ':')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace('~COMMA~', ', ')
    counts_primary_icon_type_str = counts_primary_icon_type_str.replace("'", "")

    if print_mode:
        print('Total Process Groups: ' + str(count_total))
        print('Primary Icon Type Counts: ' + counts_primary_icon_type_str)

    summary.append('There are ' + str(count_total) + ' process groups being monitored.  ' +
                   'The primary technology breakdown is ' + counts_primary_icon_type_str + '.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

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
