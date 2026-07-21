import glob
import os

from pathlib import Path


def main():
    unique_names = []
    duplicate_names = []

    file_dict = {}
    # input_glob_pattern = "../../NewPlatform/Dashboards/Downloads/NonProd/*.json"
    input_glob_pattern = "../../NewPlatform/Notebooks/Downloads/NonProd/*.json"
    for file_name in glob.glob(input_glob_pattern, recursive=True):
        if os.path.isfile(file_name) and '.metadata.' not in os.path.basename(file_name):
            path_name = Path(file_name).name.replace('DAVE SAVED', '')
            path_name = path_name.replace('DAVE SAVE', '')
            path_name = path_name.replace('DAVE RPT', '')
            path_name = path_name.replace('DAVE', '')
            path_name = path_name.replace('  SAVE', '')
            # print(path_name)
            if path_name not in unique_names:
                unique_names.append(path_name)
            else:
                duplicate_names.append((path_name))

    print('Unique Path Names')
    for unique_path_name in sorted(unique_names):
        print(unique_path_name)

    print('')
    print('Duplicate Path Names')
    for duplicate_path_name in sorted(duplicate_names):
        print(duplicate_path_name)


if __name__ == '__main__':
    main()
