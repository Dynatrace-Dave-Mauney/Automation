import os
import glob
import json


def main():
    selected_count = 0
    try:
        input_glob_pattern = "/Temp/Monaco-Renames/*.json"
        # input_glob_pattern = "/Temp/builtinmonitoring.slo/*.json"
        # input_glob_pattern = "/tools/monaco20-CNB_Prod-DOWNLOAD/download_2023-10-25-110259/project_CNB_Prod/builtinmonitoring.slo/*.json"
        # input_glob_pattern = "/tools/monaco20-CNB_Prod-DOWNLOAD/download_2023-10-26-104556/project_CNB_Prod/builtinmonitoring.slo/*.json"
        # input_glob_pattern = "/tools/monaco20-CNB_NonProd-DOWNLOAD/download_2023-11-10-100123/project_CNB_NonProd/builtinmanagement-zones/*.json"
        # input_glob_pattern = "C:/tools/monaco20-CNB_NonProd-UPDATE-Exactuals-FINAL/CNB_NonProd/builtinmanagement-zones/*.json"

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            base_file_name = os.path.basename(file_name)
            # print(base_file_name)
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    formatted_json = json.dumps(input_json, indent=4, sort_keys=False)

                    # name = input_json.get('name')
                    name = input_json.get('config-item-title')
                    enabled = input_json.get('enabled')
                    include_exclude = input_json.get('send-to-storage')
                    if include_exclude:
                        include_exclude = 'Include'
                    else:
                        include_exclude = 'Exclude'
                    json_id = input_json.get('id')
                    # metric_expression = input_json.get('metricExpression')
                    # if '- Host Availability' in name:
                    # if ' - Synthetic Availability' in name or '- Service ' in name:
                    # if 'PMTHB' in name:
                        # print(f'{name}: {metric_expression}')
                    # print(f'{name}: {base_file_name}: {enabled}')
                    # print(f'{name}|{base_file_name}|{enabled}|{include_exclude}')
                    print(f'{include_exclude}')
                    # print(formatted_json)
                    selected_count += 1
    except FileNotFoundError:
        print('The directory name does not exist')

    print(f'Total Selected: {selected_count}')


if __name__ == '__main__':
    main()
