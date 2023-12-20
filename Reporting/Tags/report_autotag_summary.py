import urllib.parse
from itertools import groupby

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def get_tag_data(env, token):
    endpoint = '/api/config/v1/autoTags'
    raw_params = 'fields=+description'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    auto_tags_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    tag_data_list = []

    for auto_tags_json in auto_tags_json_list:
        inner_auto_tags_json_list = auto_tags_json.get('values')
        for inner_auto_tags_json in inner_auto_tags_json_list:
            name = inner_auto_tags_json.get('name')
            description = inner_auto_tags_json.get('description', '')
            tag_data_list.append((name, description))

    return tag_data_list


def process(env_name_list, all_env_name_data):
    rows = []

    for key in sorted(all_env_name_data.keys()):
        autotag_data = all_env_name_data.get(key)
        autotag_name = key
        autotag_env_name_list = autotag_data.get('env_name_list')
        autotag_description_list = autotag_data.get('description_list')
        if all_equal(autotag_description_list):
            autotag_description = autotag_description_list[0]
        else:
            autotag_description = str(autotag_description_list)
        finding = ''
        if autotag_env_name_list != env_name_list or not all_equal(autotag_description_list):
            if autotag_env_name_list != env_name_list:
                finding = 'Not defined in all environments'
            else:
                finding = 'Not defined identically in all environments'

        rows.append((autotag_name, autotag_description, report_writer.stringify_list(autotag_env_name_list), finding))

    report_name = 'Auto Tag Summary'
    report_writer.initialize_text_file(None)
    report_headers = ('Auto Tag Name', 'Description', 'Environments', 'Finding')
    report_writer.write_console(report_name, report_headers, rows, delimiter='|')
    report_writer.write_text(None, report_name, report_headers, rows, delimiter='|')
    report_writer.write_xlsx(None, report_name, report_headers, rows, header_format=None, auto_filter=None)
    report_writer.write_html(None, report_name, report_headers, rows)


def add_or_update(env_name, env_name_data, all_env_name_data):
    env_name_data_current = all_env_name_data.get(env_name_data[0])
    if env_name_data_current:
        env_name_list = env_name_data_current.get('env_name_list')
        description_list = env_name_data_current.get('description_list')
        env_name_list.append(env_name)
        description_list.append(env_name_data[1])
        all_env_name_data[env_name_data[0]] = {'env_name_list': env_name_list, 'description_list': description_list}
    else:
        all_env_name_data[env_name_data[0]] = {'env_name_list': [env_name], 'description_list': [env_name_data[1]]}


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def main():
    env_name_list = ['Prod', 'NonProd']

    all_env_name_data = {}

    for env_name in env_name_list:
        env_name, env, token = environment.get_environment(env_name)
        env_name_data_list = get_tag_data(env, token)
        for env_name_data in env_name_data_list:
            add_or_update(env_name, env_name_data, all_env_name_data)

    process(env_name_list, all_env_name_data)


if __name__ == '__main__':
    main()
