import datetime

from Reuse import dynatrace_api
from Reuse import environment


def summarize(env, token):
    return process(env, token, False)


def process(env, token, print_mode):
    summary = []

    count_total = 0

    endpoint = '/api/v2/events'
    page_size = 1000
    from_time = 'now-24h'
    params = f'pageSize={page_size}&from={from_time}'
    events_json_list = dynatrace_api.get(env, token, endpoint, params)
    # print(events_json_list)

    if print_mode:
        print('Events')
        print('eventId|eventType|title|startTime|endTime|duration (D:HH:MM:SS.MMM')

    for events_json in events_json_list:
        inner_events_json_list = events_json.get('events')
        for inner_events_json in inner_events_json_list:
            # print(inner_events_json)
            event_id = inner_events_json.get('eventId')
            event_type = inner_events_json.get('eventType')
            event_title = inner_events_json.get('title')
            start_time = inner_events_json.get('startTime')
            end_time = inner_events_json.get('endTime')
            # print(f'{start_time} {end_time}')
            start_date_time = convert_epoch_in_milliseconds_to_local(start_time)
            end_date_time = convert_epoch_in_milliseconds_to_local(end_time)
            formatted_duration = format_time_duration(start_time, end_time)

            if print_mode:
                print(f'{event_id}|{event_type}|{event_title}|{start_date_time}|{end_date_time}|{formatted_duration}')

            count_total += 1

    if print_mode:
        print('Total events: ' + str(count_total))

    summary.append('There are ' + str(count_total) + ' events currently defined.')

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
