#
# Replace the main method with an improved version
#

import os
import glob
import json


def main():
    try:
        input_glob_pattern = ""
        # input_glob_pattern = "../../NewPlatform/Dashboards/Assets/External/**"
        # input_glob_pattern = "../../NewPlatform/Dashboards/Assets/*.json"
        # input_glob_pattern = "../../NewPlatform/Dashboards/Assets/External/Playground/*.json"
        # input_glob_pattern = "../../NewPlatform/Dashboards/Assets/External/TM/*.json"
        # input_glob_pattern = "../../NewPlatform/Notebooks/Assets/External/AndiG/*.json"
        # input_glob_pattern = "../../NewPlatform/Notebooks/Assets/External/Demo/*.json"
        # input_glob_pattern = "../../NewPlatform/Dashboards/Assets/External/Demo/*.json"
        # input_glob_pattern = "../../NewPlatform/Dashboards/Assets/External/AndiG/*.json"
        # input_glob_pattern = "../../NewPlatform/Notebooks/Assets/External/Playground/*.json"
        # input_glob_pattern = "../../NewPlatform/Notebooks/Assets/*.json"

        output_directory_name = '/Temp/Formatted'

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            base_file_name = os.path.basename(file_name)
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                src = file_name
                dst = os.path.join(output_directory_name, base_file_name)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(src, 'r', encoding='utf-8') as infile:
                    original_json = json.loads(infile.read())
                    formatted_json = json.dumps(original_json, indent=4, sort_keys=False)
                    with open(dst, 'w', encoding='utf-8') as outfile:
                        outfile.writelines(formatted_json)
                        print(f'Wrote {output_directory_name}/{base_file_name}')
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
