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
            dashboard_name = dashboard_name.replace(' Monitoring', '')
            dashboard_lookup[dashboard_name] = dashboard_id

    return dashboard_lookup

def write_markdown_menus(dashboard_lookup):
    menu_item_list = [
        '.NET',
        'AWS ALB',
        'AWS API Gateway',
        'AWS CloudWatch Logs',
        'AWS Cloudfront',
        'AWS Connect',
        'AWS DynamoDB',
        'AWS EBS',
        'AWS EC2',
        'AWS ECS ContainerInsights',
        'AWS ECS',
        'AWS Lambda Functions',
        'AWS Lex',
        'AWS NAT Gateways',
        'AWS NLB',
        'AWS RDS',
        'AWS Route 53 Resolver',
        'AWS Route 53',
        'AWS Site-to-Site VPN',
        'Application Overview (HTTP Monitors and Services)',
        'Application Overview (Services)',
        'Application Overview (Synthetics and Services)',
        'Application Overview (Web, HTTP Monitors, and Services)',
        'Application Overview (Web, Synthetics, and Services)',
        'Hosts (Detailed)',
        'IBM DataPower by Host',
        'IBM MQ Metrics by Best Split',
        'IBM MQ Metrics by Queue Manager and Best Split',
        'IBM MQ Metrics by Queue Manager',
        'Java',
        'Key Requests',
        'Network (Host-Level Details)',
        'Network (Process-Level Details)',
        'Processes',
        'Request Headers',
        'SAP Hana Database',
        'Service Errors',
        'Service HTTP Errors',
        'Service HTTP Errors from Non-Synthetics',
        'Service HTTP Errors from Synthetics',
        'Synthetics: Browser Monitor Events',
        'Tomcat',
        'VMware',
        'WebLogic by Name',
        'WebLogic by Process',
        'WebSphere Metrics by Pool',
        'WebSphere Metrics by Process and Pool',
        'WebSphere Metrics by Process',
    ]

    markdown_menu = '			"markdown": "More Details\\n\\n'
    for menu_item in menu_item_list:
        markdown_item_id = dashboard_lookup.get(menu_item)
        if not markdown_item_id:
            print(f'Dashboard lookup dictionary missing menu item: {menu_item}')
        markdown_menu += f'[{menu_item}](#dashboard;id={markdown_item_id})  \\n'
    markdown_menu += '"'

    filename = 'Templates/Overview/markdown_menu.json'
    with open(filename, 'w') as file:
        file.write(markdown_menu)

    aws_markdown_menu = '			"markdown": "'
    for menu_item in menu_item_list:
        if 'AWS' in menu_item:
            aws_markdown_item_id = dashboard_lookup.get(menu_item)
            if not aws_markdown_item_id:
                print(f'Dashboard lookup dictionary missing menu item: {menu_item}')
            aws_markdown_menu += f'[{menu_item}](#dashboard;id={aws_markdown_item_id})  \\n'
    markdown_menu += '"'

    filename = 'Templates/Overview/markdown_aws_menu.json'
    with open(filename, 'w') as file:
        file.write(aws_markdown_menu)



def main():
    dashboard_lookup = load_dashboard_lookup()
    # for i in dashboard_lookup:
    #     print(i)
    write_markdown_menus(dashboard_lookup)


if __name__ == '__main__':
    main()