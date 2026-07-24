import copy
import csv
import os

# Remove various prefixes from DMA Repo document metadata files
DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks'

replacements = [
    # See repair_names_in_metadata.py for example
]

# From Dynatrace Tenant Notebook (load "/lookups/splunk_index_data" Results Download to CSV)
LOOKUP_CSV = '../Lookups/downloads/lookups/splunk_index_data.csv'
SPLUNK_INDEX_COLUMN = 6
DYNATRACE_BUCKET_COLUMN = 10


def main():
    index_to_bucket_dict = {}
    with open(LOOKUP_CSV, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header row
        for row in reader:
            # print(row)
            splunk_index = row[SPLUNK_INDEX_COLUMN].lower()
            dynatrace_bucket = row[DYNATRACE_BUCKET_COLUMN]
            index_to_bucket_dict[splunk_index] = dynatrace_bucket

    try:
        input_directory_names = [DASHBOARD_REPO_PATH, NOTEBOOK_REPO_PATH]

        for input_directory_name in input_directory_names:
            #
            # input_directory_name = DASHBOARD_REPO_PATH
            # input_directory_name = NOTEBOOK_REPO_PATH
            output_directory_name = input_directory_name + '-MODIFIED'

            print(f'Converting bucket names in {input_directory_name} to {output_directory_name}')

            for file_name in os.listdir(input_directory_name):
                if os.path.isfile(f'{input_directory_name}/{file_name}') and file_name.endswith('.json') and '.metadata.' not in file_name:
                    src = f'{input_directory_name}/{file_name}'
                    dst = f'{output_directory_name}/{file_name}'
                    # print(f'Source: {src} Destination: {dst}')

                    with open(src, 'r', encoding='utf-8') as infile:
                        new_string = infile.read()
                        original_string = copy.deepcopy(new_string)

                        for replacement in replacements:
                            # Normal order
                            from_string, to_string = replacement
                            # Reversal order
                            # to_string, from_string = replacement
                            new_string = new_string.replace(from_string, to_string)

                        for index in index_to_bucket_dict.keys():
                            from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                            if from_bucket_filter in new_string:
                                bucket = index_to_bucket_dict[index]
                                print(f'Changing {index} to {bucket} for {dst}')
                                to_bucket_filter = 'bucket: {\\"' + index_to_bucket_dict[index] + '\\"}'
                                new_string = new_string.replace(from_bucket_filter, to_bucket_filter)

                        # for index in convert_to_ent_general:
                        #     from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                        #     to_bucket_filter = 'bucket: {\\"ent_general\\"}'
                        #     if from_bucket_filter in new_string:
                        #         new_string = new_string.replace(from_bucket_filter, to_bucket_filter)
                        #         # print('ent_general:', from_bucket_filter, to_bucket_filter, new_string)
                        #
                        # for index in convert_to_app_general:
                        #     from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                        #     to_bucket_filter = 'bucket: {\\"app_general\\"}'
                        #     if from_bucket_filter in new_string:
                        #         new_string = new_string.replace(from_bucket_filter, to_bucket_filter)
                        #         # print('app_general:', from_bucket_filter, to_bucket_filter, new_string)
                        #
                        # for index in convert_to_ent_os:
                        #     from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                        #     to_bucket_filter = 'bucket: {\\"ent_os\\"}'
                        #     if from_bucket_filter in new_string:
                        #         new_string = new_string.replace(from_bucket_filter, to_bucket_filter)
                        #         # print('ent_os:', from_bucket_filter, to_bucket_filter, new_string)

                        if new_string != original_string:
                            # print(f'Changed {original_string} to {new_string} for {dst}')
                            with open(dst, 'w', encoding='utf-8') as outfile:
                                outfile.write(new_string)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
