# Rename files in a directory

import os


def main():
    try:
        # directory_name = "/Temp/CURRENTCUSTOMER/NewPlatform/Dashboards/RefreshDownloaded"
        # directory_name = "../../$Private/Customers/$Current/DMA/Repo/Dashboards"
        directory_name = "../../$Private/Customers/$Current/DMA/Repo/Notebooks"
        for file_name in os.listdir(directory_name):
            if os.path.isfile(f'{directory_name}/{file_name}') and 'DAVE' in file_name and file_name.endswith('.json'):
                print(f'Renaming {directory_name}/{file_name}')
                new_file_name = file_name.replace('DAVE RPT[', '[')
                new_file_name = new_file_name.replace('DAVE SAVED[', '[')
                new_file_name = new_file_name.replace('DAVE  SAVE[', '[')
                new_file_name = new_file_name.replace('DAVE[', '[')
                src = f'{directory_name}/{file_name}'
                dst = f'{directory_name}/{new_file_name}'
                os.rename(src, dst)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
