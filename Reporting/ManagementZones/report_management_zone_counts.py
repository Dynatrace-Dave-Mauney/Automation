from Reuse import dynatrace_api
from Reuse import environment


def process(env, token):
    count_total = 0

    endpoint = '/api/config/v1/managementZones'
    params = ''
    management_zones_json_list = dynatrace_api.get(env, token, endpoint, params)

    for management_zones_json in management_zones_json_list:
        inner_management_zones_json_list = management_zones_json.get('values')
        # for inner_management_zones_json in inner_management_zones_json_list:
        for _ in inner_management_zones_json_list:
            # id = inner_management_zones_json.get('id')
            # name = inner_management_zones_json.get('name')
            count_total += 1

    # print('Total Management Zones: ' + str(count_total))

    return count_total


def main():
    print('Management Zone Counts by Tenant')
    env_name, env, token = environment.get_environment('Prod')
    total = process(env, token)
    print(env_name + ' ' + str(total))
    grand_total = total

    env_name, env, token = environment.get_environment('NonProd')
    total = process(env, token)
    print(env_name + ' ' + str(total))
    grand_total += total

    print('Grand Total: ' + str(grand_total))


if __name__ == '__main__':
    main()
