import os
import glob
import json

from Reuse import environment


def main():
    try:
        configuration_file = 'configurations.yaml'
        src = environment.get_configuration(f'summarize_json_azure_log_input_file', configuration_file=configuration_file)

        with open(src, 'r', encoding='utf-8') as infile:
            json_data = json.loads(infile.read())

            # print(json_data)

            print('Keys:')
            keys = json_data.keys()
            for key in keys:
                print(key)

            print('')
            print('Values:')
            for key in keys:
                print(f'{key}: {json_data[key]}')

    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
