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
    # ('New Platform: Shared Notebooks', 'https://{{.new_ui_tenant}}.apps.dynatrace.com/ui/document/v0/#share={{.new_ui_shared_notebooks_id}}')
    # 'New Platform: Dynatrace Architecture Launchpad',
    # 'New Platform: Dynatrace User Launchpad',
]

def load_dashboard_lookup():
    dashboard_lookup = {}

    path = 'Templates/Overview/????????-????-????-????-????????????.json'
    for filename in glob.glob(path):
        print(filename)
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
    markdown_menu = '			"markdown": "More Details\\n\\n'
    # for menu_item in menu_item_list_v1:
    # for menu_item in menu_item_list_v2:
    # for menu_item in menu_item_list_v3:
    # lower_skips = ['Redis - Home', 'F5 - Home', 'Palo Alto']

    # Combine the dashboards that have templates
    template_dashboards = sorted(main_dashboards + tech_dashboards)

    for menu_item in template_dashboards:
        # for menu_item in menu_item_list:
        markdown_item_id = dashboard_lookup.get(menu_item)
        if not markdown_item_id:
            print(f'Dashboard lookup dictionary missing menu item: {menu_item}')
            exit(1)
        # if not (env_name == 'Lower' and menu_item in lower_skips):
        if '{{.new_ui_tenant}}' in markdown_item_id:
            markdown_menu += f'[{menu_item}]({markdown_item_id})  \\n'
        else:
            markdown_menu += f'[{menu_item}](#dashboard;id={markdown_item_id})  \\n'
    markdown_menu += '"'

    filename = f'Templates/Overview/markdown_menu_{env_name}.json'
    with open(filename, 'w') as file:
        file.write(markdown_menu)

    print(f'Output File: {filename} for environment {env_name}')


def main():
    dashboard_lookup = load_dashboard_lookup()
    # for i in dashboard_lookup:
    #     print(i)
    write_markdown_menus(dashboard_lookup)


if __name__ == '__main__':
    main()

    # History for Reference if ever needed...
    # 
    # Current Customer list
    # menu_item_list_v4 = [
    #     'Administration',
    #     'Application Overview - Home',
    #     'Backend Overview',
    #     'Calls To Databases',
    #     'Containers',
    #     'Detailed Drilldowns Menu',
    #     'Dynatrace-owned Dashboards',
    #     'Full Stack Overview',
    #     'Hosts (Detailed)',
    #     'Key Requests',
    #     'Key User Actions',
    #     'Monitoring Overview',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'Processes',
    #     'Queues',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Suspicious Activity Audit',
    #     'Synthetics: Browser Monitor Events',
    #     'Third Party Services',
    # ]
    # 
    # menu_item_list_v4 = [
    #     '.NET',
    #     'Administration',
    #     'Application Overview - Home',
    #     'AWS Home',
    #     'Backend Overview',
    #     'Calls To Databases',
    #     'CICS',
    #     'Cloud Foundry',
    #     'Containers',
    #     'ControlM',
    #     'Custom PMI Metrics',
    #     'DB2 - Home',
    #     'Detailed Drilldowns Menu',
    #     'Executor',
    #     'F5 - Home',
    #     'Full Stack Overview',
    #     'Go',
    #     'HikariCP',
    #     'Hosts (Detailed)',
    #     'IBM MQ Home',
    #     'IBM WebSphere Home',
    #     # 'IBM MQ Metrics by Best Split',
    #     # 'IBM MQ Metrics by Queue Manager and Best Split',
    #     # 'IBM MQ Metrics by Queue Manager',
    #     'Java',
    #     'Java Memory',
    #     'Kafka Home',
    #     # 'Kafka - Home',
    #     'Key Requests',
    #     'Key User Actions',
    #     'Kubernetes - Home',
    #     'Microsoft Exchange',
    #     'Microsoft SQL Server',
    #     'Monitoring Overview',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'New Platform: Shared Notebooks',
    #     'NGIS',
    #     'Node.js',
    #     'Processes',
    #     'Queues',
    #     'R2DBC',
    #     'Resilience4j',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Snowflake',
    #     'Spark',
    #     'Spring',
    #     'Suspicious Activity Audit',
    #     'Synthetics: Browser Monitor Events',
    #     'Third Party Services',
    #     'Tomcat',
    #     'VMware',
    #     'Web Application Insights',
    #     'Web Servers',
    # ]
    #
    # Demo
    # menu_item_list = [
    #     '.NET',
    #     'Administration',
    #     'Application Overview (HTTP Monitors and Services)',
    #     'Application Overview (Services)',
    #     'Application Overview (Synthetics and Services)',
    #     'Application Overview (Web, HTTP Monitors, and Services)',
    #     'Application Overview (Web, Synthetics, and Services)',
    #     'Detailed Drilldowns Menu',
    #     'Full Stack Overview',
    #     'Hosts (Detailed)',
    #     'Java',
    #     'Java Memory',
    #     'Kafka - Home',
    #     'Key Requests',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'Processes',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Service HTTP Errors from Non-Synthetics',
    #     'Service HTTP Errors from Synthetics',
    #     'Synthetics: Browser Monitor Events',
    #     'Tomcat',
    #     'VMware',
    #     'Web Servers',
    # ]
    #
    # # Customer1-specific list
    # menu_item_list_v1 = [
    #     '.NET',
    #     'Administration',
    #     'AWS Home',
    #     'Application Overview (HTTP Monitors and Services)',
    #     'Application Overview (Services)',
    #     'Application Overview (Synthetics and Services)',
    #     'Application Overview (Web, HTTP Monitors, and Services)',
    #     'Application Overview (Web, Synthetics, and Services)',
    #     'Detailed Drilldowns Menu',
    #     'Full Stack Overview',
    #     'Hosts (Detailed)',
    #     'IBM DataPower by Host',
    #     'IBM DataPower Overview',
    #     'IBM MQ Metrics by Best Split',
    #     'IBM MQ Metrics by Queue Manager and Best Split',
    #     'IBM MQ Metrics by Queue Manager',
    #     'IBM WebSphere Metrics by Pool',
    #     'IBM WebSphere Metrics by Process and Pool',
    #     'IBM WebSphere Metrics by Process',
    #     'Java',
    #     'Java Memory',
    #     'Kafka - Home',
    #     'Key Requests',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'Processes',
    #     'SAP Hana Database',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Service HTTP Errors from Non-Synthetics',
    #     'Service HTTP Errors from Synthetics',
    #     'Synthetics: Browser Monitor Events',
    #     'Tomcat',
    #     'VMware',
    #     'Web Servers',
    #     'WebLogic by Name',
    #     'WebLogic by Process',
    # ]
    #
    # # Customer2-specific list
    # menu_item_list_v2 = [
    #     '.NET',
    #     'Administration',
    #     'Application Overview - Home',
    #     'Azure - Home',
    #     'Backend Overview',
    #     'Containers',
    #     'Detailed Drilldowns Menu',
    #     'Full Stack Overview',
    #     'Go',
    #     'Hosts (Detailed)',
    #     'Java',
    #     'Java Memory',
    #     'Jetty',
    #     'Key Requests',
    #     'Kubernetes - Home',
    #     'Microsoft SQL Server - Home',
    #     'Monitoring Overview',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'Node.js',
    #     'Oracle Database - Home',
    #     'Processes',
    #     'SOLR',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Suspicious Activity Audit',
    #     'Synthetics: Browser Monitor Events',
    #     'Tomcat',
    #     'Web Servers',
    #     'WebLogic by Name',
    #     'WebLogic by Process',
    #     'WebSphere',
    # ]
    #
    # Customer3-specific list
    # menu_item_list_v3 = [
    #     '.NET',
    #     'Administration',
    #     'Application Overview - Home',
    #     'Backend Overview',
    #     'Containers',
    #     'Detailed Drilldowns Menu',
    #     'Full Stack Overview',
    #     'Go',
    #     'Hosts (Detailed)',
    #     'Java',
    #     'Java Memory',
    #     'Key Requests',
    #     'Key User Actions',
    #     'Kubernetes - Home',
    #     'Monitoring Overview',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'Node.js',
    #     'Processes',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Suspicious Activity Audit',
    #     'Synthetics: Browser Monitor Events',
    #     'Tomcat',
    #     'Web Application Insights',
    #     'Web Servers',
    #     'WebLogic by Name',
    #     'WebLogic by Process',
    # ]
    # Customer3-specific list
    # menu_item_list_v4 = [
    #     '.NET',
    #     'Administration',
    #     'Application Overview - Home',
    #     'Azure - Home',
    #     'Backend Overview',
    #     'Calls To Databases',
    #     'Containers',
    #     'Detailed Drilldowns Menu',
    #     'F5 - Home',
    #     'Full Stack Overview',
    #     'Go',
    #     'Hosts (Detailed)',
    #     'Java',
    #     'Java Memory',
    #     'Kafka - Home',
    #     'Key Requests',
    #     'Key User Actions',
    #     'Kubernetes - Home',
    #     'Microsoft SQL Server - Home',
    #     'Monitoring Overview',
    #     'Network (Host-Level Details)',
    #     'Network (Process-Level Details)',
    #     'Node.js',
    #     'Palo Alto',
    #     'Processes',
    #     'Queues',
    #     'Redis - Home',
    #     'Service Errors',
    #     'Service HTTP Errors',
    #     'Suspicious Activity Audit',
    #     'Synthetics: Browser Monitor Events',
    #     'Tomcat',
    #     'VMware',
    #     'Web Application Insights',
    #     'Web Servers',
    # ]
