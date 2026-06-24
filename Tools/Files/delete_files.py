#
# Delete files matching criteria
#

import os
import glob


def main():
    count = 0
    delete_list = []
    # input_glob_pattern = "../../Reporting/**"
    input_glob_pattern = "../../$Private/$Output/Dashboards/ClassicConversionMetaData/*.json"
    for file_name in glob.glob(input_glob_pattern, recursive=True):
        if os.path.isfile(file_name) and not file_name.endswith('.metadata.json'):
            delete_list.append(file_name)

    if len(delete_list) > 0:
        print('FILES TO BE DELETED: ')
        for line in delete_list:
            print(line)

        msg = 'PROCEED WITH DELETE OF LISTED FILES?'
        proceed = input("%s (Y/n) " % msg).upper() == 'Y'

        if proceed:
            for line in delete_list:
                os.remove(line)
                print('DELETED: ' + line)
                count += 1

            print('Files Deleted: ' + str(count))
    else:
        print('Nothing to do!')

if __name__ == '__main__':
    main()
