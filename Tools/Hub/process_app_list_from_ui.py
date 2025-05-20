#
# Navigate to Apps, Explore More, Click All link, then  select Type App.
# Highlight sections at a time and save to text file (app_list_from_ui.txt)
# Run this module to summarize.
#

import requests
from bs4 import BeautifulSoup

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process_app_list_from_ui():
    apps = []
    filename = 'app_list_from_ui.txt'
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            apps.append(line.strip())

    index = 0
    for app in apps:
        if 'icon' in app:
            root_index = index + 1
            if apps[root_index + 1] not in ['Installed', 'Coming Soon']:
                if 'AWS' not in apps[root_index] and 'Amazon' not in apps[root_index]:
                    app_name = apps[root_index]
                    app_desc = apps[root_index+2]
                    print(f'{app_name}: {app_desc}')
        index += 1


def main():
    process_app_list_from_ui()


if __name__ == '__main__':
    main()

