# Rename files in a directory

import os
# import os.path
# from os import path


def main():
    try:
        directory_name = "../../Dashboards/Templates/Overview"
        for file_name in os.listdir(directory_name):
            if os.path.isfile(f'{directory_name}/{file_name}') and file_name.startswith('00000000-dddd-bbbb-ffff') and not file_name.endswith('.json'):
                print(f'Renaming {directory_name}/{file_name}')
                src = f'{directory_name}/{file_name}'
                dst = f'{directory_name}/{file_name}.json'
                os.rename(src, dst)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
