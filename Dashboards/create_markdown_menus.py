# Create the markdown menu for the "Overview Dashboard".
#

import codecs
import glob
import json

env_name = 'Prod'

# These will work with any customer, and are in the templates directory
main_dashboards = [
    'Administration',
    # 'Application Overview - Home',
    # 'Backend Overview',
    # 'Calls To Databases',
    # 'Containers',
    'Detailed Drilldowns Menu',
    'Dynatrace-owned Dashboards',
    # 'Full Stack Overview',
    'Hosts (Detailed)',
    # 'Key Requests',
    # 'Key User Actions',
    # 'Monitoring Overview',
    'NetApp OnTap',
    'Network (Host-Level Details)',
    'Network (Process-Level Details)',
    # 'Processes',
    'Pure Storage FlashArray',
    # 'Queues',
    # 'Service Errors',
    # 'Service HTTP Errors',
    # 'Suspicious Activity Audit',
    # 'Synthetics: Browser Monitor Events',
    # 'Third Party Services',
]

# These differ by customer, and are in the templates directory
tech_dashboards = [
    # '.NET',
    # 'Go',
    # 'Java',
    # 'Java Memory',
    # 'Kubernetes - Home',
    # 'Node.js',
    # 'Tomcat',
    # 'Web Servers',
]


# These differ by customer, and are not in the templates directory
ootb_dashboards = [
    # ('Palo Alto', 'ab163c60-07f5-7e82-40d5-35cd6a8be991')
]

# These differ by customer, and are not in the templates directory
new_ui_dashboards = [
    ('Gen 3 Dynatrace User Launchpad', 'https://{{.tenant}}.apps.dynatrace.com/ui/apps/dynatrace.launcher/launchpad/bce5a9a6-bdc6-4b3f-9e9d-314dadc36461'),
    ('Gen 3 Dynatrace Architecture Launchpad', 'https://{{.tenant}}.apps.dynatrace.com/ui/apps/dynatrace.launcher/launchpad/945124d7-14d1-4b3e-9e7b-95dad889978d'),
    ('Gen 3 Overview Dashboard', 'https://{{.tenant}}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/57b60014-c4ab-45f0-89e5-e4409a52734c'),
    ('Gen 3 Overview by Management Zone Dashboard', 'https://{{.tenant}}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/d3673a3e-27ca-48c2-b534-8fb2edb906a2'),
]


def load_dashboard_lookup():
    dashboard_lookup = {}

    path = 'Templates/Overview/????????-????-????-????-????????????.json'
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = json.loads(f.read())
            dashboard_id = dashboard['id']
            dashboard_name = dashboard.get('dashboardMetadata').get('name').replace('TEMPLATE: ', '')
            dashboard_name = dashboard_name.replace(' Monitoring', '')
            dashboard_lookup[dashboard_name] = dashboard_id

    for ootb_dashboard in ootb_dashboards:
        dashboard_name = ootb_dashboard[0]
        dashboard_id = ootb_dashboard[1]
        dashboard_lookup[dashboard_name] = dashboard_id

    for new_ui_link in new_ui_dashboards:
        link_name = new_ui_link[0]
        link_url = new_ui_link[1]
        dashboard_lookup[link_name] = link_url

    return dashboard_lookup


def write_markdown_menus(dashboard_lookup):
    links = []

    markdown_menu = '			"markdown": "More Details\\n\\n'

    # Combine the dashboards that have templates
    template_dashboards = sorted(main_dashboards + tech_dashboards)

    for menu_item in template_dashboards:
        markdown_item_id = dashboard_lookup.get(menu_item)
        if not markdown_item_id:
            print(f'Dashboard lookup dictionary missing menu item: {menu_item}')
            exit(1)
        links.append((menu_item, f'#dashboard;id={markdown_item_id}'))

    for ootb_item in ootb_dashboards:
        links.append((ootb_item[0], f'#dashboard;id={ootb_item[1]}'))

    for new_ui_item in new_ui_dashboards:
        links.append((new_ui_item[0], new_ui_item[1]))

    for menu_item in links:
        markdown_menu += f'[{menu_item[0]}]({menu_item[1]})  \\n'
    markdown_menu += '"'

    filename = f'Templates/Overview/markdown_menu_{env_name}.json'
    with open(filename, 'w') as file:
        file.write(markdown_menu)

    print(f'Output File: {filename} for environment {env_name}')


def main():
    dashboard_lookup = load_dashboard_lookup()
    write_markdown_menus(dashboard_lookup)


if __name__ == '__main__':
    main()
