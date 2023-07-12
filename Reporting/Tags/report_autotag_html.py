import urllib.parse
from datetime import date

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer

env_name = ''

html_file_path = '../../$Output/Reporting'


def process(env, token):
    endpoint = '/api/config/v1/autoTags'
    raw_params = 'fields=+description'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    auto_tags_json_list = dynatrace_api.get(env, token, endpoint, params)

    rows = []

    html_file_name = f'{html_file_path}/TagSummary_For_{env_name}.html'

    for auto_tags_json in auto_tags_json_list:
        inner_auto_tags_json_list = auto_tags_json.get('values')
        for inner_auto_tags_json in inner_auto_tags_json_list:
            name = inner_auto_tags_json.get('name')
            description = inner_auto_tags_json.get('description', '')
            rows.append((name, description))

    write_console(sorted(rows))
    write_html(html_file_name, sorted(rows))

    print(f'Output written to {html_file_name}')


def write_console(rows):
    today = date.today()
    run_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)
    title = f'Dynatrace Tag Summary for {env_name} As Of {run_date}'
    headers = ('Tag Name', 'Tag Description')
    delimiter = '|'
    report_writer.write_console(title, headers, rows, delimiter)


def write_html(html_file_name, rows):
    today = date.today()
    run_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)
    page_heading = f'Dynatrace Tag Summary for {env_name} As Of {run_date}'
    table_headers = ('Tag Name', 'Tag Description')
    report_writer.write_html(html_file_name, page_heading, table_headers, rows)


def main():
    global env_name

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

    process(env, token)


if __name__ == '__main__':
    main()
