import glob
import time
from zipfile import ZipFile

def main(env):
    timestr = time.strftime("%Y%m%d-%H%M%S")

    with ZipFile('C:\Backups\DynatraceDashboardGeneratorBackup_' + env + '_' + timestr + '.zip', 'w') as zip_file:
        print(f'creating zip archive: {zip_file.filename}')

        paths = ['*.py', '*.yaml', '*.json', '*.txt', '*.md', '*.db']
        # for f in file_list:
        print(f'backing up paths: {paths}')
        for path in paths:
            print(f'backing up path: {path}')
            for f in glob.glob(path):
                print(f'adding {f}')
                zip_file.write(f)

        print(f'successfully created archive: {zip_file.filename }')

if __name__ == '__main__':
    main('MANUAL')
