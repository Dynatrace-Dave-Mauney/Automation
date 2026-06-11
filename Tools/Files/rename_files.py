# Rename files in a directory

import os


def main():
    try:
        directory_name = "/Temp/CURRENTCUSTOMER/NewPlatform/Dashboards/RefreshDownloaded"
        for file_name in os.listdir(directory_name):
            if os.path.isfile(f'{directory_name}/{file_name}') and 'TEMPLATE' in file_name and file_name.endswith('.json'):
                print(f'Renaming {directory_name}/{file_name}')
                new_file_name = file_name.replace('TEMPLATE', 'Prod')
                src = f'{directory_name}/{file_name}'
                dst = f'{directory_name}/{new_file_name}'
                os.rename(src, dst)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
