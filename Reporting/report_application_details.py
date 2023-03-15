import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/entities'
    raw_params = 'pageSize=4000&entitySelector=type(APPLICATION)&fields=+properties&to=-5m'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    entities_json_list = dynatrace_api.get(env, token, endpoint, params)
    if print_mode:
        print('entityId' + '|' + 'displayName' + '|' + 'detectedName' + '|' + 'applicationType' + '|' + 'ruleAppliedMatchType' + '|' + 'applicationInjectionType' + '|' + 'applicationMatchTarget' + '|' + 'ruleAppliedPattern' + '|' + 'customizedName')
        print(entities_json_list[0])
    for entities_json in entities_json_list:
        # print(entities_json)
        inner_entities_json_list = entities_json.get('entities')
        for inner_entities_json in inner_entities_json_list:
            entity_id = inner_entities_json.get('entityId')
            display_name = inner_entities_json.get('displayName')

            properties = inner_entities_json.get('properties')

            detected_name = properties.get('detectedName', '')
            application_type = properties.get('applicationType', '')
            rule_applied_match_type = properties.get('ruleAppliedMatchType', '')
            application_injection_type = properties.get('applicationInjectionType', '')
            application_match_target = properties.get('applicationMatchTarget', '')
            rule_applied_pattern = properties.get('ruleAppliedPattern', '')
            customized_name = properties.get('customizedName', '')

            if print_mode:
                print(entity_id + '|' + display_name + '|' + detected_name + '|' + application_type + '|' + rule_applied_match_type + '|' + application_injection_type + '|' + application_match_target + '|' + rule_applied_pattern + '|' + customized_name)

            count_total += 1

    if print_mode:
        print('Total applications: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' web applications currently defined and reporting data.')

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
