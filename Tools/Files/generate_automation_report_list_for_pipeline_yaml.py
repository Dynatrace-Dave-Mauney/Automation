import glob
import os.path

ignore_list = [
    'dynatrace_rest_api_helper.py',
    'findings_loader.py',
    'perform_report_details_testing.py',
    'perform_summarize_environment_html.py',
    'perform_summarize_environment_print.py',
    'report_activegate_details_standalone.py',
    'Dashboards/dashboard_views.py',
    'Dashboards/mda_dashboard_reference_check.py',
    'Entities/report_entities_with_specific_technology_icons.py',
    'Entities/report_process_group_instances_with_specific_technology_versions.py',
    'Logs/report_logs_per_process_group_to_excel.py',
    'ManagementZones/management_zone_reference_check.py',
    'ManagementZones/report_management_zone_coverage.py',
    'Settings20/compare_oneagent_features_by_tenant.py',
    'Synthetics/estimate_synthetic_consumption.py',
    'Tags/auto_tag_reference_check.py',
    'Tags/report_autotag_html.py',
    'Tags/report_autotag_summary_html.py',
    'Tags/report_monitored_entity_custom_tags_details.py',
]

def find_matching_py_files():
    for filename in glob.glob('../../Reporting/**/*.py', recursive=True):
        with open(filename, 'r', encoding='utf-8') as f:
            report_name = filename.replace('../../Reporting\\', '').replace('\\', '/')
            if report_name not in ignore_list:
                print(f'  - {report_name},')

def main():
    find_matching_py_files()


if __name__ == '__main__':
    main()
