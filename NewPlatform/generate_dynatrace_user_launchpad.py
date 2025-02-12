import codecs
import copy
import json
import re

from Reuse import environment
from Reuse import new_platform_api

launchpad_template = {
    "schemaVersion": 2,
    "icon": "default",
    "background": "default",
    "containerList": {
        "containers": [
            {
                "blocks": [],
                "horizontalLayoutWeight": 1
            }
        ]
    }
}

launchpad_markdown_block_template = {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "type": "markdown",
    "properties": {
        "expanded": True
    },
    "content": ""
}

launchpad_link_block_template = {
    "id": "aaaaaaaa-bbbb-cccc-dddd-ffffffffffff",
    "type": "links",
    "properties": {
        "expanded": True
    },
    "appearance": "tile",
    "title": "xyz",
    "description": "",
    "contentType": "static",
    "content": [
        {
            "id": "b678165d-b598-4a1f-bed4-5d9db0530c88",
            "type": "doc",
            "title": "Network devices performance ",
            "action": {
                "type": "openDocument",
                "documentId": "d15625d5-2911-455a-a95b-4e2da3bdff21"
            },
            "icon": "",
            "categoryId": "dashboards"
        }
    ]
}


def process(env_name, env, client_id, client_secret):
    tenant_name = env_name.capitalize()
    tenant = env.replace('https://', '')
    tenant = re.sub(r'\..*', '', tenant)

    shared_launchpad = launchpad_template
    shared_launchpad_blocks = shared_launchpad['containerList']['containers'][0]['blocks']
    shared_launchpad_blocks.append(generate_application_block())
    shared_launchpad_blocks.append(generate_ready_made_dashboard_links_block(env, client_id, client_secret))
    shared_launchpad_blocks.append(generate_documentation_block('Dashboards', get_dashboard_links(tenant_name, tenant)))
    shared_launchpad_blocks.append(generate_documentation_block('Dynatrace User Documentation', get_documentation_links()))
    shared_launchpad_blocks.append(generate_documentation_block('Dynatrace University', get_university_links()))
    write_launchpad(shared_launchpad)


def get_dashboard_links(tenant_name, tenant):
    links = [
        (f'{tenant_name} Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cf48719e-9e5f-42b1-902e-d118cabbe6df'),
        (f'{tenant_name} Services',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6ef4c6cb-7fc0-4871-bebe-4c527fe8da03'),
        (f'{tenant_name} Service Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9cf2cdec-e883-4497-a365-b4fd047a7cd8'),
        (f'{tenant_name} Service HTTP Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f0ad8bd8-4cdd-4ec6-a483-13eed9074761'),
        (f'{tenant_name} Synthetics HTTP Monitors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=14784246-597a-475a-b950-35c3602ded84'),
        (f'{tenant_name} Hosts (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8b56dbd9-598c-412b-927e-426ec8465cb2'),
        (f'{tenant_name} Hosts',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a6295b0a-0d82-42b2-a430-c0e7b69cf85c'),
        (f'{tenant_name} Network (Host-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d8f2e522-f16b-4666-bdef-6a63a18b54b4'),
        (f'{tenant_name} Network (Process-Level Details)',
         'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c5ac91a0-3037-41db-bdd5-2e4deaf6a382'),
        (f'{tenant_name} VMware',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=62dd2a66-3bf9-4e62-a7e3-759006a79453'),
        (f'{tenant_name} Containers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d87c28fa-b052-425a-acbd-e42684b63bdb'),
        (f'{tenant_name} Full Stack Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=43509742-c2e9-44a5-a501-fb9c75b45264'),
        (f'{tenant_name} Backend Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b9b6498c-222a-4eaf-9025-e344c9e3f183'),
        (f'{tenant_name} Java Memory',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f373d6f4-2138-41b3-b9c1-8355c52b0b1b'),
        (f'{tenant_name} Go',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=26568803-df30-4999-bc50-748ce1df22ce'),
        (f'{tenant_name} Node.js',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4a98b69e-826c-400b-a17a-80aaabdb9089'),
        (f'{tenant_name} Web Servers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0845de3e-ef7e-46f0-b65a-32e4504b1f24'),
    ]

    return links


def get_documentation_links():
    links = [
        ('What is Dynatrace', 'https://docs.dynatrace.com/docs/shortlink/intro'),
        ('Navigate the Dynatrace platform', 'https://docs.dynatrace.com/docs/shortlink/navigation'),
        ('Platform search', 'https://docs.dynatrace.com/docs/shortlink/platform-search'),
        ('Dashboards', 'https://docs.dynatrace.com/docs/shortlink/dashboards'),
        ('Notebooks', 'https://docs.dynatrace.com/docs/shortlink/notebooks'),
        ('Launchpads', 'https://docs.dynatrace.com/docs/shortlink/launchpads'),
        ('Dynatrace Apps', 'https://docs.dynatrace.com/docs/shortlink/dynatrace-apps'),
        ('Dynatrace Developer', 'https://developer.dynatrace.com/'),
        ('Introduction to workflows', 'https://docs.dynatrace.com/docs/shortlink/workflows'),
        ('Dynatrace Query Language', 'https://docs.dynatrace.com/docs/shortlink/dql-dynatrace-query-language-hub'),
        ('Dynatrace Pattern Language', 'https://docs.dynatrace.com/docs/shortlink/dpl-dynatrace-pattern-language-hub'),
        ('Dashboards Classic', 'https://docs.dynatrace.com/docs/shortlink/dashboards-hub'),
        ('Services App', 'https://docs.dynatrace.com/docs/shortlink/services-app'),
        ('Services', 'https://docs.dynatrace.com/docs/shortlink/services'),
        ('Service analysis (classic page)', 'https://docs.dynatrace.com/docs/shortlink/services-analysis'),
        ('Databases', 'https://docs.dynatrace.com/docs/shortlink/databases-hub'),
        ('Message queues', 'https://docs.dynatrace.com/docs/shortlink/queues-hub'),
        ('Distributed Tracing', 'https://docs.dynatrace.com/docs/shortlink/distributed-traces-grail'),
        ('Log Content Analysis', 'https://docs.dynatrace.com/docs/shortlink/lma-analysis'),
        ('Metrics', 'https://docs.dynatrace.com/docs/shortlink/metrics-grail'),
        ('Profiling and optimization', 'https://docs.dynatrace.com/docs/shortlink/profiling-optimization'),
        ('Real User Monitoring concepts', 'https://docs.dynatrace.com/docs/shortlink/basic-concepts-landing'),
        ('Web applications', 'https://docs.dynatrace.com/docs/shortlink/web-applications-landing'),
        ('Session segmentation', 'https://docs.dynatrace.com/docs/shortlink/user-sessions-landing'),
        ('Session Replay', 'https://docs.dynatrace.com/docs/shortlink/session-replay'),
        ('Synthetic Monitoring', 'https://docs.dynatrace.com/docs/shortlink/synthetic-hub'),
        ('Problems app', 'https://docs.dynatrace.com/docs/shortlink/davis-ai-problems-app'),
        ('Process groups', 'https://docs.dynatrace.com/docs/shortlink/processes-hub'),
        ('Analyze processes', 'https://docs.dynatrace.com/docs/shortlink/process-analysis'),
        ('Hosts', 'https://docs.dynatrace.com/docs/shortlink/hosts-hub'),
        ('Host monitoring with Dynatrace', 'https://docs.dynatrace.com/docs/shortlink/host-monitoring'),
        ('Networks', 'https://docs.dynatrace.com/docs/shortlink/network-hub'),
        ('How to monitor network communications', 'https://docs.dynatrace.com/docs/shortlink/network-monitoring'),
    ]

    return links


def get_university_links():
    links = [
        ('Beginner Level', 'https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=beginner'),
        ('Intermediate Level', 'https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=intermediate'),
        ('Advanced Level', 'https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=advanced'),
    ]

    return links


def generate_documentation_block(block_name, documentation_links):
    launchpad_block = copy.deepcopy(launchpad_markdown_block_template)
    shared_markdown_string = f'#  {block_name}  \n'

    for documentation_link in documentation_links:
        documentation_link_markdown = f'[{documentation_link[0]}]({documentation_link[1]})  \n'
        shared_markdown_string += documentation_link_markdown

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def generate_ready_made_dashboard_links_block(env, client_id, client_secret):
    launchpad_block = copy.deepcopy(launchpad_link_block_template)
    new_launchpad_block_content = []
    dashboard_link_list = get_ready_made_dashboard_links(env, client_id, client_secret)
    for dashboard_link in dashboard_link_list:
        launchpad_block_content = copy.deepcopy(launchpad_block.get('content')[0])
        launchpad_block_content['title'] = dashboard_link[0]
        launchpad_block_content['action']['documentId'] = dashboard_link[1]
        new_launchpad_block_content.append(launchpad_block_content)

    launchpad_block['title'] = 'Dynatrace Ready Made Dashboards'
    launchpad_block['content'] = new_launchpad_block_content

    return launchpad_block


def get_ready_made_dashboard_links(env, client_id, client_secret):
    selected_ready_made_dashboards = [
        'AWS overview',
        'ActiveGate diagnostic overview',
        'Azure overview',
        'Cisco Device Overview',
        'Databases Overview',
        'Extension Data Consumption',
        'F5 BIG-IP DNS Overview',
        'F5 BIG-IP LTM Overview',
        'F5 BIG-IP LTM Status',
        'Getting started',
        'IBM Datapower Overview',
        'IBM MQ Monitoring Overview',
        'Infrastructure Observability Dashboard',
        'Kafka Overview',
        'Kubernetes Cluster',
        'Kubernetes Namespace - Pods',
        'Kubernetes Namespace - Workloads',
        'Kubernetes Node - Pods',
        'Kubernetes Persistent Volumes',
        'Log ingest overview',
        'Log query usage and costs',
        'Network analytics',
        'Network availability monitoring',
        'Network devices',
        'Network performance',
        'Nutanix Overview',
        'Oracle DB Overview',
        'SQL Server Overview',
        'Salesforce Data Ingest Overview',
        'Salesforce Ingest and Outage',
        'Salesforce Overview',
        'Salesforce Pages with Timeouts',
        'Salesforce User Activity Deep Dive',
        'VMware Extension Overview',
        'Web availability and performance',
    ]
    dynatrace_owner = 'ed29e85d-9e5f-4157-a2b8-563dc624708f'

    scope = 'document:documents:read'

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
    documents_json = json.loads(results.text)
    document_list = documents_json.get('documents')
    rows = []
    for document in document_list:
        document_type = document.get('type')
        if document_type == 'dashboard':
            document_id = document.get('id')
            document_name = document.get('name')
            document_owner = document.get('owner')

            if document_owner == dynatrace_owner:
                if document_name in selected_ready_made_dashboards:
                    rows.append([document_name, document_id])

    return sorted(rows)


def generate_application_block():
    selected_apps = [
        'Launcher',
        'Dashboards',
        'Dashboards Classic',
        'Notebooks',
        'Workflows',
        'Problems',
        'Problems Classic',
        'Services',
        'Services Classic',
        'Databases',
        'Database Services Classic',
        'Distributed Tracing',
        'Distributed Traces Classic',
        'Technologies & Processes Classic',
        'Multidimensional Analysis',
        'Data Explorer',
        'Extensions',
        'Extensions Classic',  # FIXED title to avoid duplication
        'Logs',
        'Logs & Events Classic',
        'Segments',
        'AWS overview',
        'AWS Classic',
        'Azure overview',
        'Azure Classic',
        'Service-Level Objectives',
        'Service-Level Objectives Classic',
        'Hosts Classic',
        'Host Networking',
        'VMware Classic',
        'Infrastructure & Operations',
    ]

    app_dict = {}
    filename = 'Launchpads/Assets/QuickApplicationLinks.json'
    with codecs.open(filename, encoding='utf-8') as f:
        document = f.read()
        document_json = json.loads(document)
        block = document_json.get('containerList').get('containers')[0].get('blocks')[0]
        block_content_list = block.get('content')
        if block_content_list:
            for link in block_content_list:
                link_title = link.get('title')
                # link_id = link.get('id')
                # link_action_app_id = link.get('appId')
                # link_icon = link.get('icon')
                # print(link_title, link_id, link_action_app_id, link_icon)
                # print(f"\t'{link_title}',")
                app_dict[link_title] = link

    launchpad_block = copy.deepcopy(block)
    new_block_content_list = []

    for selected_app in selected_apps:
        link = app_dict[selected_app]
        new_block_content_list.append(link)

    launchpad_block['content'] = new_block_content_list
    return launchpad_block


def write_launchpad(launchpad_json):
    with open('Dynatrace User Launchpad.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(launchpad_json, indent=4, sort_keys=False))


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'QA'
    # env_name_supplied = 'UAT'
    # env_name_supplied = 'SIT'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Demo'
    # env_name_supplied = 'Personal'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env_name, env, client_id, client_secret)


if __name__ == '__main__':
    main()
