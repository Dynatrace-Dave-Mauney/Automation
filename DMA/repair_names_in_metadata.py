import os

# Remove various prefixes from DMA Repo document metadata files
DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks'


replacements = [
    ('DAVE[', '['),
    ('DAVE RPT[', '['),
    ('DAVE SAVED[', '['),
    ('DAVE  SAVE[', '['),
]

def main():
    try:
        input_directory_name = DASHBOARD_REPO_PATH
        input_directory_name = NOTEBOOK_REPO_PATH
        # output_directory_name = input_directory_name + '-MODIFIED'
        output_directory_name = input_directory_name

        for file_name in os.listdir(input_directory_name):
            if os.path.isfile(f'{input_directory_name}/{file_name}') and file_name.endswith('.metadata.json'):
                src = f'{input_directory_name}/{file_name}'
                dst = f'{output_directory_name}/{file_name}'

                with open(src, 'r', encoding='utf-8') as infile:
                    new_string = infile.read()
                    for replacement in replacements:
                        # Normal order
                        from_string, to_string = replacement
                        # Reversal order
                        # to_string, from_string = replacement
                        new_string = new_string.replace(from_string, to_string)
                    print(f'{src} {dst} {from_string} {to_string}')
                    with open(dst, 'w', encoding='utf-8') as outfile:
                        outfile.write(new_string)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
