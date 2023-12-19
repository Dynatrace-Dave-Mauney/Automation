import glob
import os


def main():
    file_dict = {}
    input_glob_pattern = "C:\\Test\\**"
    for file_name in glob.glob(input_glob_pattern, recursive=True):
        if os.path.isfile(file_name) and '.' in os.path.basename(file_name):
            base_name = os.path.basename(file_name)
            extension = base_name.split('.')[-1]
            new_list = file_dict.get(extension, [])
            new_list.append(file_name)
            file_dict[extension] = new_list

    for extension in sorted(file_dict.keys()):
        print(f'Files with extension: {extension}')
        for file_name in sorted(file_dict.get(extension)):
            print(file_name)
        print('')


if __name__ == '__main__':
    main()
