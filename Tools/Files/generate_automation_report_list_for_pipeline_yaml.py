import glob
import os.path

ignore_list = [
    'dynatrace_rest_api_helper.py',
    'findings_loader.py',
    'perform_report_details_testing.py',
    'perform_summarize_environment_html.py',
    'perform_summarize_environment_print.py',
]

def find_matching_py_files():
    for filename in glob.glob('../../Reporting/**/*.py', recursive=True):
        with open(filename, 'r', encoding='utf-8') as f:
            report_name = filename.replace('../../Reporting\\', '').replace('\\', '/')
            if report_name not in ignore_list:
                print(f'  - {report_name}')

def main():
    find_matching_py_files()


if __name__ == '__main__':
    main()
