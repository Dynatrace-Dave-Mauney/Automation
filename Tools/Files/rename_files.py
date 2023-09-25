# Rename files in a directory

import os
# import os.path
# from os import path


def main():
    try:
        directory_name = "../../NewPlatform/Dashboards"
        for file_name in os.listdir(directory_name):
            if os.path.isfile(f'{directory_name}/{file_name}') and '- ' in file_name and file_name.endswith('.json'):
                print(f'Renaming {directory_name}/{file_name}')
                new_file_name = file_name.replace('- ', ' - ')
                src = f'{directory_name}/{file_name}'
                dst = f'{directory_name}/{new_file_name}'
                os.rename(src, dst)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
