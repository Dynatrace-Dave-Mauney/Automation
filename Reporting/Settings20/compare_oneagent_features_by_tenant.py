import os
import urllib.parse
import xlsxwriter

from Reuse import dynatrace_api
from Reuse import environment

env_name_list = ['Prod', 'NonProd']

SETTING_NOT_FOUND = '⛔'
SETTING_ENABLED = '✔'
SETTING_DISABLED = 'X'

# SETTING_NOT_FOUND = 'None'
# SETTING_ENABLED = 'On'
# SETTING_DISABLED = 'Off'


def process_oneagent_features(env_name, env, token, all_env_name_data):
    endpoint = '/api/v2/settings/objects'
    schema_ids = 'builtin:oneagent.features'
    schema_ids_param = f'schemaIds={schema_ids}'
    raw_params = schema_ids_param + '&scopes=environment&fields=schemaId,value,Summary&pageSize=500'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    settings_object_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)

    for settings_object in settings_object_list:
        items = settings_object.get('items', [])

        lines = []

        if items:
            for item in items:
                value = item.get('value')
                summary = item.get('summary').replace('\\', '')
                enabled = value.get('enabled')
                cryptic_key = value.get('key')
                feature_name = f'{summary} ({cryptic_key})'
                lines.append(f'{feature_name}:{enabled}')

                feature_dict = all_env_name_data.get(feature_name, {})
                feature_dict[env_name] = enabled
                all_env_name_data[feature_name] = feature_dict

        return all_env_name_data


def write_xlsx(all_env_name_data):
    output_directory = environment.get_output_directory_name('.')
    xlsx_file_name = os.path.join(output_directory, 'OneAgentFeaturesTenantComparison.xlsx')

    workbook = xlsxwriter.Workbook(xlsx_file_name)
    header_format = workbook.add_format({'bold': True, 'bg_color': '#B7C9E2'})

    bold_red_font = workbook.add_format({'bold': True, 'font_color': 'red'})
    bold_green_font = workbook.add_format({'bold': True, 'font_color': 'green'})

    # Worksheet 1 of 3
    worksheet = workbook.add_worksheet('OneAgent Feature Differences')

    row_index = 0
    column_index = 0

    headers = ['Feature']

    for env_name in env_name_list:
        headers.append(env_name)

    for _ in headers:
        worksheet.write(row_index, column_index, headers[column_index], header_format)
        column_index += 1

    row_index += 1
    column_index = 0

    for key in sorted(all_env_name_data.keys()):
        feature_dict = all_env_name_data.get(key, {})
        if has_differences(feature_dict):
            worksheet.write(row_index, column_index, key)
            column_index += 1
            for env_name in env_name_list:
                feature_by_env = feature_dict.get(env_name)
                feature_indicator = get_feature_indicator(feature_by_env)
                if feature_indicator == SETTING_ENABLED:
                    worksheet.write(row_index, column_index, feature_indicator, bold_green_font)
                else:
                    if feature_indicator == SETTING_DISABLED:
                        worksheet.write(row_index, column_index, feature_indicator, bold_red_font)
                    else:
                        if feature_indicator == SETTING_NOT_FOUND:
                            worksheet.write(row_index, column_index, feature_indicator, bold_red_font)
                column_index += 1
            row_index += 1
            column_index = 0

    worksheet.autofilter(0, 0, row_index, len(env_name_list))  # add filter to all columns
    worksheet.autofit()

    # Worksheet 2 of 3
    worksheet = workbook.add_worksheet('OneAgent Features Summary')

    row_index = 0
    column_index = 0

    headers = ['Feature']

    for env_name in env_name_list:
        headers.append(env_name)

    for _ in headers:
        worksheet.write(row_index, column_index, headers[column_index], header_format)
        column_index += 1

    row_index += 1
    column_index = 0

    for key in sorted(all_env_name_data.keys()):
        worksheet.write(row_index, column_index, key)
        column_index += 1
        feature_dict = all_env_name_data.get(key, {})
        for env_name in env_name_list:
            feature_by_env = feature_dict.get(env_name)
            feature_indicator = get_feature_indicator(feature_by_env)
            if feature_indicator == SETTING_ENABLED:
                worksheet.write(row_index, column_index, feature_indicator, bold_green_font)
            else:
                if feature_indicator == SETTING_DISABLED:
                    worksheet.write(row_index, column_index, feature_indicator, bold_red_font)
                else:
                    if feature_indicator == SETTING_NOT_FOUND:
                        worksheet.write(row_index, column_index, feature_indicator, bold_red_font)
            column_index += 1
        row_index += 1
        column_index = 0

    worksheet.autofilter(0, 0, row_index, len(env_name_list))  # add filter to all columns
    worksheet.autofit()

    # Worksheet 3 of 3
    worksheet = workbook.add_worksheet('Legend')

    headers = ['Feature Enabled', 'Feature Disabled', 'Feature Not Available']
    worksheet.write(0, 0, headers[0], header_format)
    worksheet.write(0, 1, headers[1], header_format)
    worksheet.write(0, 2, headers[2], header_format)
    worksheet.write(1, 0, SETTING_ENABLED, bold_green_font)
    worksheet.write(1, 1, SETTING_DISABLED, bold_red_font)
    worksheet.write(1, 2, SETTING_NOT_FOUND, bold_red_font)
    worksheet.autofit()

    workbook.close()

    print(f'Output written to {xlsx_file_name}')


def get_feature_indicator(feature_by_env):
    if feature_by_env is None:
        return SETTING_NOT_FOUND
    else:
        if feature_by_env:
            return SETTING_ENABLED
        else:
            return SETTING_DISABLED


def has_differences(feature_dict):
    # since we don't know each key is present, convert to list first then check list for equal values
    compare_list = []
    for env_name in env_name_list:
        compare_list.append(feature_dict.get(env_name))

    # converting the list to a set is an easy way to check if all values are equal since duplicates are removed
    # https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
    return len(set(compare_list)) > 1


def main():
    all_env_name_data = {}

    for env_name in env_name_list:
        env_name, env, token = environment.get_environment(env_name)
        process_oneagent_features(env_name, env, token, all_env_name_data)

    # for key in sorted(all_env_name_data.keys()):
    #     print(key, str(all_env_name_data.get(key)))

    write_xlsx(all_env_name_data)


if __name__ == '__main__':
    main()
