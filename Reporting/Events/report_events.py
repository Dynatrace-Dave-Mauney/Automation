import datetime

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def summarize(env, token):
    return process_report(env, token, True)


def process(env, token):
    return process_report(env, token, False)


def process_report(env, token, summary_mode):
    rows = []
    summary = []

    count_total = 0

    endpoint = '/api/v2/events'
    page_size = 1000
    from_time = 'now-24h'
    params = f'pageSize={page_size}&from={from_time}'
    events_json_list = dynatrace_api.get(env, token, endpoint, params)

    for events_json in events_json_list:
        inner_events_json_list = events_json.get('events')
        for inner_events_json in inner_events_json_list:
            event_id = inner_events_json.get('eventId')
            event_type = inner_events_json.get('eventType')
            event_title = inner_events_json.get('title')
            start_time = inner_events_json.get('startTime')
            end_time = inner_events_json.get('endTime')
            start_date_time = report_writer.convert_epoch_in_milliseconds_to_local(start_time)
            end_date_time = report_writer.convert_epoch_in_milliseconds_to_local(end_time)
            formatted_duration = format_time_duration(start_time, end_time)

            if not summary_mode:
                rows.append((event_type, event_title, start_date_time, end_date_time, formatted_duration, event_id))

            count_total += 1

    summary.append('There are ' + str(count_total) + ' events currently defined.')

    if not summary_mode:
        rows = sorted(rows)
        report_name = 'Events'
        report_writer.initialize_text_file(None)
        report_headers = ('eventType', 'title', 'startTime', 'endTime', 'duration (D:HH:MM:SS.MMM)', 'eventId')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Events: ' + str(count_total)])
        write_strings(summary)
        report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
        report_writer.write_html(None, report_name, report_headers, rows)

    return summary


def write_strings(string_list):
    report_writer.write_console_plain_text(string_list)
    report_writer.write_plain_text(None, string_list)


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


def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
