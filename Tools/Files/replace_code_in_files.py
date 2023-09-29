#
# Replace the main method with an improved version
#

import os
import glob


replacement_lines = '''def main():
    friendly_function_name = 'Dynatrace Automation Reporting'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
    process(env, token, True)
    
    
'''


def main():
    try:
        input_glob_pattern = "../../Reporting/**"
        output_directory_name = '/Temp/Modified_Code'

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.py'):
                src = file_name
                dst = f"{output_directory_name}/{file_name.replace('../../', '')}"
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                print(file_name)
                with open(src, 'r', encoding='utf-8') as infile:
                    new_lines = []
                    index = 0
                    main_start = 9999
                    main_end = 9999
                    old_lines = infile.readlines()
                    for old_line in old_lines:
                        if 'def main():' in old_line:
                            main_start = index
                            # print(f'main_start: {main_start}')
                        if 'if __name__' in old_line:
                            main_end = index
                            # print(f'main_end: {main_end}')
                        # print(f'index: {index}')
                        if index < main_start or index >= main_end:
                            new_lines.append(old_line)
                        if index == main_start:
                            new_lines.append(replacement_lines)
                        index += 1
                    with open(dst, 'w', encoding='utf-8') as outfile:
                        outfile.writelines(new_lines)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
