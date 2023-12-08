#
# Delete report output files
#

import os
import glob

oddball_list = [
    '../../Reporting/Dashboards/dashboard_views.html',
    '../../Reporting/Dashboards/dashboard_views.txt',
    '../../Reporting/Dashboards/dashboard_views.xlsx',
    '../../Reporting/Dashboards/mda_dashboard_reference_check.html',
    '../../Reporting/Dashboards/mda_dashboard_reference_check.txt',
    '../../Reporting/Dashboards/mda_dashboard_reference_check.xlsx',
    '../../Reporting/ManagementZones/management_zone_reference_check.html',
    '../../Reporting/ManagementZones/management_zone_reference_check.txt',
    '../../Reporting/ManagementZones/management_zone_reference_check.xlsx',
    '../../Reporting/Settings20/OneAgentFeaturesTenantComparison.xlsx',
    '../../Reporting/Settings20/Settings20EnvironmentScopeTenantComparison.xlsx',
    '../../Reporting/Settings20/Settings20EnvironmentScopeTenantDiffs.txt',
    '../../Reporting/Synthetics/estimate_synthetic_consumption.html',
    '../../Reporting/Synthetics/estimate_synthetic_consumption.txt',
    '../../Reporting/Synthetics/estimate_synthetic_consumption.xlsx',
    '../../Reporting/Tags/auto_tag_reference_check.html',
    '../../Reporting/Tags/auto_tag_reference_check.txt',
    '../../Reporting/Tags/auto_tag_reference_check.xlsx',
    '../../Reporting/analyze_audit_log_details.html',
    '../../Reporting/analyze_audit_log_details.txt',
    '../../Reporting/analyze_audit_log_details.xlsx',
]

def main():
    count = 0
    delete_list = []

    # append_to_delete_list(delete_list, '../../Reporting/**/report_*.html')
    # append_to_delete_list(delete_list, '../../Reporting/**/report_*.txt')
    # append_to_delete_list(delete_list, '../../Reporting/**/report_*.xlsx')

    # Use to find oddballs...just choose "N" to skip the delete and then add them to the oddball_list
    # append_to_delete_list(delete_list, '../../Reporting/**/*.html')
    # append_to_delete_list(delete_list, '../../Reporting/**/*.txt')
    # append_to_delete_list(delete_list, '../../Reporting/**/*.xlsx')

    # delete_list.extend(oddball_list)
    for oddball in oddball_list:
        if os.path.isfile(oddball):
            delete_list.append(oddball)

    if len(delete_list) > 0:
        print('FILES TO BE DELETED: ')
        for line in delete_list:
            print(line)

        msg = 'PROCEED WITH DELETE OF LISTED FILES?'
        proceed = input("%s (Y/n) " % msg).upper() == 'Y'

        if proceed:
            for line in delete_list:
                if os.path.isfile(line):
                    os.remove(line)
                    print('DELETED: ' + line)
                    count += 1
                else:
                    print('FILE DOES NOT EXIST: ' + line)

            print('Files Deleted: ' + str(count))
    else:
        print('Nothing to do!')


def append_to_delete_list(delete_list, glob_pattern):
    for file_name in glob.glob(glob_pattern, recursive=True):
        if os.path.isfile(file_name):
            delete_list.append(file_name)


if __name__ == '__main__':
    main()
