from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/config/v1/aws/credentials'
    params = ''
    aws_credentials_json_list = dynatrace_api.get(env, token, endpoint, params)

    if print_mode:
        print('id' + '|' + 'name')

    for aws_credentials_json in aws_credentials_json_list:
        entity_id = aws_credentials_json.get('id')
        name = aws_credentials_json.get('name')

        if print_mode:
            print(entity_id + '|' + name)

        count_total += 1

    if print_mode:
        print('Total AWS Accounts: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' AWS accounts currently configured.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)
        

def main():
    # env_name, env, token = environment.get_environment('Prod')
    # env_name, env, token = environment.get_environment('Prep')
    # env_name, env, token = environment.get_environment('Dev')
    env_name, env, token = environment.get_environment('Personal')
    # env_name, env, token = environment.get_environment('FreeTrial1')

    process(env, token, True)


if __name__ == '__main__':
    main()
