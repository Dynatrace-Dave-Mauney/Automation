import datetime

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/problems'
    page_size = 10
    from_time = 'now-30d'
    fields = 'evidenceDetails,impactAnalysis'
    problem_selector = 'managementZones("")'
    severity_level = 'severityLevel("RESOURCE_CONTENTION")'
    params = f'pageSize={page_size}&from={from_time}&fields={fields}&problemSelector={problem_selector}&severityLevel={severity_level}'
    problems_json_list = dynatrace_api.get(env, token, endpoint, params)
    print(problems_json_list)

    if print_mode:
        print('Problems')
        print('displayId|startTime|endTime|duration (D:HH:MM:SS.MMM|affectedEntities|rootCauseEntity')

    for problems_json in problems_json_list:
        inner_problems_json_list = problems_json.get('problems')
        for inner_problems_json in inner_problems_json_list:
            # print(inner_problems_json)
            # problem_id = inner_problems_json.get('problemId')
            display_id = inner_problems_json.get('displayId')
            # problem_type = inner_problems_json.get('problemType')
            # problem_title = inner_problems_json.get('title')
            start_time = inner_problems_json.get('startTime')
            end_time = inner_problems_json.get('endTime')
            # print(f'{start_time} {end_time}')
            start_date_time = convert_epoch_in_milliseconds_to_local(start_time)
            end_date_time = convert_epoch_in_milliseconds_to_local(end_time)
            formatted_duration = format_time_duration(start_time, end_time)

            affected_entities_list = []
            affected_entities = inner_problems_json.get('affectedEntities')
            for affected_entity in affected_entities:
                affected_entity_name = affected_entity.get('name')
                affected_entities_list.append(affected_entity_name)
            formatted_affected_entities = str(sorted(affected_entities_list)).replace('[', '').replace(']', '').replace("'", "")

            root_cause_entity = inner_problems_json.get('rootCauseEntity')
            if root_cause_entity:
                formatted_root_cause_entity = root_cause_entity.get('name')

            if print_mode:
                print(f'{display_id}|{start_date_time}|{end_date_time}|{formatted_duration}|{formatted_affected_entities}|{formatted_root_cause_entity}')

            count_total += 1

    if print_mode:
        print('Total problems: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' problems currently defined.')

    if print_mode:
        print_list(summary)
        print('Done!')

    return summary


def format_time_duration(start_time, end_time):
    if end_time == -1:
        return 'ONGOING'
    else:
        duration = (end_time - start_time) // 1000
        millis = str(duration)[-3:]
        days = hours = minutes = 0
        if duration > 86400:
            days = duration // 86400
            duration -= days * 86400
        if duration > 3600:
            hours = duration // 3600
            duration -= hours * 3600
        if duration > 60:
            minutes = duration // 60
            duration -= minutes * 60
        formatted_time_duration = f'{days}:{hours:02d}:{minutes:02d}:{duration:02d}.{millis}'
        return formatted_time_duration


def print_list(any_list):
    for line in any_list:
        line = line.replace('are 0', 'are no')
        print(line)


def convert_epoch_in_milliseconds_to_local(epoch):
    if epoch == -1:
        return None
    else:
        return datetime.datetime.fromtimestamp(epoch / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


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
