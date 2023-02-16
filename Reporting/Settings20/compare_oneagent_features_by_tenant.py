import dynatrace_rest_api_helper
import os
import urllib.parse
import xlsxwriter

supported_environments = {
    'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
}

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
    settings_object = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)[0]
    items = settings_object.get('items', [])

    lines = []

    if items:
        for item in items:
            value = item.get('value')
            summary = item.get('summary').replace('\\', '')
            enabled = value.get('enabled')
            lines.append(f'{summary}:{enabled}')

            feature_dict = all_env_name_data.get(summary, {})
            feature_dict[env_name] = enabled
            all_env_name_data[summary] = feature_dict

        return all_env_name_data


def get_environment(env_name):
    if env_name not in supported_environments:
        print(f'Invalid environment name: {env_name}')
        return env_name, None, None

    tenant_key, token_key = supported_environments.get(env_name)

    if env_name and tenant_key and token_key:
        tenant = os.environ.get(tenant_key)
        token = os.environ.get(token_key)
        env = f'https://{tenant}.live.dynatrace.com'

        if tenant and token and '.' in token:
            masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'
            print(f'Environment Name: {env_name}')
            print(f'Environment:      {env}')
            print(f'Token:            {masked_token}')
            return env_name, env, token
        else:
            print('Invalid Environment Configuration!')
            print(f'Set the "env_name ({env_name}), tenant_key ({tenant_key}), token_key ({token_key})" tuple as required and verify the tenant ({tenant}) and token ({token}) environment variables are accessible.')
            exit(1)


def write_xlsx(all_env_name_data):
    workbook = xlsxwriter.Workbook('../../$Output/Reporting/Settings20/OneAgentFeaturesTenantComparison.xlsx')
    header_format = workbook.add_format({'bold': True, 'bg_color': '#B7C9E2'})

    bold_red_font = workbook.add_format({'bold': True, 'font_color': 'red'})
    bold_green_font = workbook.add_format({'bold': True, 'font_color': 'green'})

    # Worksheet 1 of 3
    worksheet = workbook.add_worksheet('OneAgent Feature Differences')

    row_index = 0
    column_index = 0

    headers = ['Feature']

    for supported_environment in supported_environments:
        headers.append(supported_environment)

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
            for supported_environment in supported_environments:
                feature_by_env = feature_dict.get(supported_environment)
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

    worksheet.autofilter(0, 0, row_index, len(supported_environments))  # add filter to all columns
    worksheet.autofit()

    # Worksheet 2 of 3
    worksheet = workbook.add_worksheet('OneAgent Features Summary')

    row_index = 0
    column_index = 0

    headers = ['Feature']

    for supported_environment in supported_environments:
        headers.append(supported_environment)

    for _ in headers:
        worksheet.write(row_index, column_index, headers[column_index], header_format)
        column_index += 1

    row_index += 1
    column_index = 0

    for key in sorted(all_env_name_data.keys()):
        worksheet.write(row_index, column_index, key)
        column_index += 1
        feature_dict = all_env_name_data.get(key, {})
        for supported_environment in supported_environments:
            feature_by_env = feature_dict.get(supported_environment)
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

    worksheet.autofilter(0, 0, row_index, len(supported_environments))  # add filter to all columns
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
    for supported_environment in supported_environments:
        compare_list.append(feature_dict.get(supported_environment))

    # converting the list to a set is an easy way to check if all values are equal since duplicates are removed
    # https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
    return len(set(compare_list)) > 1


def main():
    env_name_list = ['Prod', 'Prep', 'Dev']

    all_env_name_data = {}

    for env_name in env_name_list:
        env_name, env, token = get_environment(env_name)
        process_oneagent_features(env_name, env, token, all_env_name_data)

    # for key in sorted(all_env_name_data.keys()):
    #     print(key, str(all_env_name_data.get(key)))

    write_xlsx(all_env_name_data)


if __name__ == '__main__':
    main()