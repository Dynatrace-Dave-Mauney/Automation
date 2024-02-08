"""
Update problem notification integration as specified.
"""
import argparse
import copy
import json

from Reuse import dynatrace_api
from Reuse import environment


endpoint = '/api/config/v1/notifications'
selected_problem_notification_ids = {
    'Prod': [],
    'PreProd': [],
    'Dev': ['feaf4f5a-d5eb-34fe-b362-f158bd733623'],
    'Sandbox': [],
}


def process(env_name, env, token, field_name, field_value):
    selected_problem_notification_id_list = selected_problem_notification_ids.get(env_name, [])
    for selected_problem_notification_id in selected_problem_notification_id_list:
        url = f'{env}{endpoint}/{selected_problem_notification_id}'
        r = dynatrace_api.get_without_pagination(url, token)
        selected_problem_notification = r.json()
        print(selected_problem_notification)
        old_field_value = selected_problem_notification.get(field_name)
        selected_problem_notification[field_name] = field_value
        dynatrace_api.put_object(url, token, json.dumps(selected_problem_notification))
        print(f'Field "{field_name}" changed from "{old_field_value}" to "{field_value}"')


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-fn", "--field_name", help="Notification JSON Field Name ('active')")
    arg_parser.add_argument("-fv", "--field_value", help="Notification JSON Value for Field Name ('True|False')")
    # Keep a pristine copy of arg_parser for later
    my_arg_parser = copy.deepcopy(arg_parser)

    # args = environment.args_parser(arg_parser=arg_parser)

    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name, arg_parser=arg_parser)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name, arg_parser=my_arg_parser)

    args = my_arg_parser. parse_args()
    if args.field_name and args.field_value:
        process(env_name, env, token, args.field_name, args.field_value)


if __name__ == '__main__':
    main()
