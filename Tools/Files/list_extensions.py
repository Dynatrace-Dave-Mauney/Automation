
import glob
import os


def main():
    extension_list = []
    try:
        input_glob_pattern = "../../**"
        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and '.' in os.path.basename(file_name):
                extension = file_name.split('.')[-1]
                if extension not in extension_list:
                    extension_list.append(extension)
    except FileNotFoundError:
        print('The directory name does not exist')

    for extension in sorted(extension_list):
        print(extension)


if __name__ == '__main__':
    main()
