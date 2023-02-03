# Create the markdown menu for the "Overview Dashboard".
#

import codecs
import glob
import json
import pathlib

def load_dashboard_lookup():
    dashboard_lookup = {}

    path = 'Templates/Overview/????????-????-????-????-????????????'
    for filename in glob.glob(path):
        with codecs.open(filename, encoding='utf-8') as f:
            dashboard = json.loads(f.read())
            dashboard_id = dashboard['id']
            dashboard_name = dashboard.get('dashboardMetadata').get('name').replace('TEMPLATE: ', '')
            dashboard_lookup[dashboard_name] = dashboard_id

    return dashboard_lookup

def write_markdown_menu(dashboard_lookup):
    menu_item_list = [
        'Processes',
        'Java Monitoring',
        '.NET Monitoring',
        'Tomcat Monitoring',
        'Service Errors',
        'Service HTTP Errors',
        'Service HTTP Errors from Non-Synthetics',
        'Service HTTP Errors from Synthetics',
        'Key Requests',
        'Network (Host-Level Details)',
        'Network (Process-Level Details)',
        'Hosts (Detailed)',
        'Application Overview (Web, Synthetics, and Services)',
        'Application Overview (Web, HTTP Monitors, and Services)',
        'Application Overview (Synthetics and Services)',
        'Application Overview (HTTP Monitors and Services)',
        'Application Overview (Services)',
        'Synthetics: Browser Monitor Events',
        'F5',
        'IBM DataPower by Host',
        'IBM MQ Metrics by Queue Manager',
        'IBM MQ Metrics by Best Split',
        'IBM MQ Metrics by Queue Manager and Best Split',
        'WebSphere Metrics by Process',
        'WebSphere Metrics by Pool',
        'WebSphere Metrics by Process and Pool',
        'WebLogic by Name',
        'WebLogic by Process',
        'SAP Hana Database',
        'VMware',
        'Request Headers',
        'AWS - ALB',
        'AWS - CLB',
        'AWS - DynamoDB',
        'AWS - EBS',
        'AWS - EC2',
        'AWS - Lambda Functions',
        'AWS - NLB',
        'AWS - RDS',
        'AWS API Gateway',
        'AWS Cloudfront',
        'Amazon CloudWatch Logs',
        'Amazon Connect',
        'AWS ECS',
        'AWS ECS ContainerInsights',
        'Amazon Lex',
        'AWS NAT Gateways',
        'Amazon Route 53',
        'AWS Route 53 Resolver',
        'AWS Site-to-Site VPN',
    ]
    # menu_item_list = [
    #     'AWS - ALB',
    #     'AWS - CLB',
    #     'AWS - DynamoDB',
    #     'AWS - EBS',
    #     'AWS - EC2',
    #     'AWS - Lambda Functions',
    #     'AWS - NLB',
    #     'AWS - RDS',
    # ]
    markdown_menu = '			"markdown": "More Details\\n\\n'
    for menu_item in menu_item_list:
        markdown_item_id = dashboard_lookup.get(menu_item)
        if not markdown_item_id:
            print(f'Dashboard lookup dictionary missing menu item: {menu_item}')
        markdown_menu += f'[{menu_item}](#dashboard;id={markdown_item_id})  \\n'
    markdown_menu += '"'

    # filename = 'Templates/Overview/markdown_aws_basic_menu.json'
    filename = 'Templates/Overview/markdown_menu.json'
    with open(filename, 'w') as file:
        file.write(markdown_menu)


def main():
    dashboard_lookup = load_dashboard_lookup()
    # for i in dashboard_lookup:
    #     print(i)
    write_markdown_menu(dashboard_lookup)


if __name__ == '__main__':
    main()
