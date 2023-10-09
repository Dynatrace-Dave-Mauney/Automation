import glob
# import os.path

ignore_list = [
    'dynatrace_rest_api_helper.py',
    'findings_loader.py',
    'perform_report_details_testing.py',
    'perform_summarize_environment_html.py',
    'perform_summarize_environment_print.py',
    'report_activegate_certificate_details.py',
    'report_activegate_oneagent_communication_comparison_details.py',
    'report_aws_credential_details.py',
    'report_aws_credential_details_specific_customer.py',
    'report_aws_supporting_service_details.py',
    'report_deployment_api_details.py',
    'report_host_group_details_customer_specific.py',
    'AWS/EC2/report_aws_ec2_hosts.py',
    'Dashboards/mda_dashboard_reference_check.py',
    'DeploymentAPI/report_deployment_api_details.py',
]


def find_matching_py_files():
    for filename in glob.glob('../../Reporting/**/*.py', recursive=True):
        with open(filename, 'r', encoding='utf-8'):
            report_name = filename.replace('../../Reporting\\', '').replace('\\', '/')
            if report_name not in ignore_list:
                print(f'  - {report_name}')


def main():
    find_matching_py_files()


if __name__ == '__main__':
    main()
