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

    endpoint = '/api/v2/problems'
    page_size = 10
    # from_time = 'now-30d'
    from_time = 'now-24h'
    fields = 'evidenceDetails,impactAnalysis'
    problem_selector = 'managementZones()'
    severity_level = 'severityLevel()'
    params = f'pageSize={page_size}&from={from_time}&fields={fields}&problemSelector={problem_selector}&severityLevel={severity_level}'
    problems_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for problems_json in problems_json_list:
        inner_problems_json_list = problems_json.get('problems')
        for inner_problems_json in inner_problems_json_list:
            # problem_id = inner_problems_json.get('problemId')
            display_id = inner_problems_json.get('displayId')
            # problem_type = inner_problems_json.get('problemType')
            # problem_title = inner_problems_json.get('title')
            start_time = inner_problems_json.get('startTime')
            end_time = inner_problems_json.get('endTime')
            start_date_time = report_writer.convert_epoch_in_milliseconds_to_local(start_time)
            end_date_time = report_writer.convert_epoch_in_milliseconds_to_local(end_time)
            formatted_duration = format_time_duration(start_time, end_time)

            affected_entities_list = []
            affected_entities = inner_problems_json.get('affectedEntities')
            for affected_entity in affected_entities:
                affected_entity_name = affected_entity.get('name')
                affected_entities_list.append(affected_entity_name)
            formatted_affected_entities = str(sorted(affected_entities_list)).replace('[', '').replace(']', '').replace("'", "")

            root_cause_entity = inner_problems_json.get('rootCauseEntity')
            formatted_root_cause_entity = ''
            if root_cause_entity:
                formatted_root_cause_entity = root_cause_entity.get('name')

            if not summary_mode:
                rows.append((display_id, start_date_time, end_date_time, formatted_duration, formatted_affected_entities, formatted_root_cause_entity))

            count_total += 1

    summary.append(f'There are {str(count_total)} problems in the timeframe ({from_time})')

    if not summary_mode:
        report_name = 'Problems'
        report_writer.initialize_text_file(None)
        report_headers = ('displayId', 'startTime', 'endTime', 'duration (D:HH:MM:SS.MMM', 'affectedEntities', 'rootCauseEntity')
        report_writer.write_console(report_name, report_headers, rows, delimiter='|')
        report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
        write_strings(['Total Problems: ' + str(count_total)])
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token)
    
    
if __name__ == '__main__':
    main()
