import os
import glob
import json

from Reuse import environment


def main():
    try:
        configuration_file = 'configurations.yaml'
        src = environment.get_configuration(f'summarize_json_input_file', configuration_file=configuration_file)
        dst_dir = environment.get_configuration(f'summarize_json_output_directory', configuration_file=configuration_file)

        base_file_name = os.path.basename(src)

        dst = os.path.join(dst_dir, base_file_name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, 'r', encoding='utf-8') as infile:
            notebook = json.loads(infile.read())

            print(notebook)

            sections = notebook['sections']
            print(sections)

            try:
                for section in sections:
                    print(section['state']['input']['value'])
            except KeyError:
                    print('null')

            # formatted_json = json.dumps(original_json, indent=4, sort_keys=False)
            # with open(dst, 'w', encoding='utf-8') as outfile:
            #     outfile.writelines(formatted_json)
            #     print(f'Wrote {dst}')
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
