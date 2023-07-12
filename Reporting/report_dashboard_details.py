from Reuse import dynatrace_api
from Reuse import environment


filter_by_owner = False
target_owner = 'nobody@example.com'

filter_by_id_starts_with = False
id_starts_with_list = ['00000000-dddd-bbbb-ffff']

filter_by_id_not_starts_with = False
id_not_starts_with_list = []
# id_not_starts_with_list = [
#     '00000000-dddd-bbbb-aaaa', # Curated/Sandbox/Alpha [VETTED]
#     '00000000-dddd-bbbb-eeee', # AWS Supporting Services (Dynatrace Owner) [VETTED]
#     'aaaaaaaa-0001', # Licensing Overview and Children [VETTED]
#     'aaaaaaaa-0002', # 3rd Party XHR Detection [VETTED]
#     'aaaaaaaa-bbbb-cccc-aaaa', # Billing, Host Health Breakdown [VETTED]
#     'aaaaaaaa-bbbb-cccc-dddd-1', # Dynatrace Dashboard Generator [VETTED]
#     'aaaaaaaa-bbbb-cccc-eeee-f', # AWS Supporting Services (Improved) [VETTED]
#     'aaaaaaaa-bbbb-cccc-ffff', # Curated/Kafka [MERGED]
#     'aaaaaaaa-ffff-ffff-ffff', # Dynatrace Self-Monitoring [VETTED]
#     # Customer-specific manually created dashboards
#     '64350c11-5cc5-46d9-b0ec-4a8b7dd78ac0',  # Amazon Connect Details (copy: 00000000-dddd-bbbb-aaaa-000000000006)
#     '98d1533a-9d05-4d06-b207-fdb15d55a54d',  # Contact Center (copy: 00000000-dddd-bbbb-aaaa-000000000007)
#     'bc9a70df-31fc-49af-9953-badf3f9b82ca', # User Engagement
# ]

def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0
    count_dynatrace_owned = 0

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id|name|owner')

    lines = []

    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            dashboard_id = inner_dashboards_json.get('id')
            name = inner_dashboards_json.get('name')
            owner = inner_dashboards_json.get('owner')

            if print_mode:
                if not filter_by_owner or (filter_by_owner and target_owner in owner):
                    if not filter_by_id_starts_with or (filter_by_id_starts_with and id_starts_with_match(dashboard_id)):
                        if not filter_by_id_not_starts_with or (filter_by_id_not_starts_with and id_not_starts_with_match(dashboard_id)):
                            lines.append(f'{dashboard_id}|{name}|{owner}')

            if not filter_by_owner or (filter_by_owner and target_owner in owner):
                if not filter_by_id_starts_with or (filter_by_id_starts_with and id_starts_with_match(dashboard_id)):
                    if not filter_by_id_not_starts_with or (filter_by_id_not_starts_with and id_not_starts_with_match(dashboard_id)):
                        count_total += 1

            if not filter_by_owner and not filter_by_id_starts_with and not filter_by_id_not_starts_with and owner == 'Dynatrace':
                count_dynatrace_owned += 1

    if print_mode:
        for line in sorted(lines):
            print(line)

    if print_mode:
        print('Total Dashboards:   ' + str(count_total))
        if not filter_by_owner:
            print('Dynatrace Created:  ' + str(count_dynatrace_owned))
            summary.append('There are ' + str(count_total) + ' dashboards currently defined.  ' + str(count_dynatrace_owned) + ' were created by Dynatrace.')
        else:
            summary.append('There are ' + str(count_total) + ' dashboards currently defined owned by ' + target_owner)

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def id_starts_with_match(dashboard_id):
    for id_starts_with in id_starts_with_list:
        if dashboard_id.startswith(id_starts_with):
            return True

    return False


def id_not_starts_with_match(dashboard_id):
    # Tricky due to double negation, but basically if the dashboard id is in the "must not start with" list,
    # return False as it DOES start with the string
    for id_not_starts_with in id_not_starts_with_list:
        if dashboard_id.startswith(id_not_starts_with):
            return False

    return True


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'FreeTrial1'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token, True)
    
    
if __name__ == '__main__':
    main()
