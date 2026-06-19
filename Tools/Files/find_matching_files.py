import glob


def find_matching_py_files():
    for filename in glob.glob('../../**/*.py'):
        with open(filename, 'r', encoding='utf-8') as f:
            # print(f'Checking {filename}')
            content = f.read()
            if 'raw_params' in content and 'urllib.parse.quote' not in content:
                print(filename)

            # if 'Dynatrace Automation' in content:
            #     if "'Dynatrace Automation'" not in content and 'Dynatrace Automation Reporting' not in content and 'Dynatrace Automation Tools' not in content  and 'Dynatrace Automation Token Management' not in content:
            #         print(filename)


def find_classic_dashboards_without_overview_link():
    for filename in glob.glob('../../Dashboards/Templates/Overview/00000000-dddd-bbbb-ffff-????????????.json'):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)' not in content:
                print('Missing Overview Link:', filename)


def main():
    # find_matching_py_files()
    find_classic_dashboards_without_overview_link()


if __name__ == '__main__':
    main()
