import os
import glob
import json

from Reuse import environment


def main():
    try:
        configuration_file = 'configurations.yaml'
        src = environment.get_configuration(f'summarize_json_azure_log_based_properties_file', configuration_file=configuration_file)

        with open(src, 'r', encoding='utf-8') as infile:
            json_data = json.loads(infile.read())

            for json_dict in json_data:
                name = json_dict['displayName']
                query = json_dict['criteria']['allOf'][0]['query']
                # print(json_dict.keys())

                if 'traces' not in query:
                    print(name)
                    print(query)
                    print('')


    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
