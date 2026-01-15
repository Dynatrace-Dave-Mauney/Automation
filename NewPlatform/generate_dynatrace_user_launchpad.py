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
    # shared_launchpad_blocks.append(generate_ready_made_dashboard_links_block(env, client_id, client_secret))
    shared_launchpad_blocks.append(generate_documentation_block('Dashboards', get_dashboard_links(tenant_name, tenant)))
    shared_launchpad_blocks.append(generate_documentation_block('Dynatrace User Documentation', get_documentation_links()))
    shared_launchpad_blocks.append(generate_documentation_block('Dynatrace University', get_university_links()))
    write_launchpad(shared_launchpad)


def get_dashboard_links(tenant_name, tenant):

    # Use add_environment_shares.py and generate_shared_document_links.py
    # to generate these lists

    prod_links = [
        (f'{tenant_name}: Overview (Classic Dashboard)',
         f'https://{tenant}.live.dynatrace.com/#dashboard;id=00000000-dddd-bbbb-ffff-000000000001'),
        (f'{tenant_name} Backend Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2e9b5aa4-9380-4dc4-a5d7-42c3febb9808'),
        (f'{tenant_name} Backend Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=36730483-b704-444e-a5ff-15359903437a'),
        (f'{tenant_name} Containers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=11c84247-ce60-4292-8ee3-562a4887a7f4'),
        (f'{tenant_name} Containers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=93755756-640a-449c-950e-8a999267d85b'),
        (f'{tenant_name} Full Stack Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=489491b5-a999-435a-81bf-3a03f2353207'),
        (f'{tenant_name} Full Stack Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0416be3a-4dc2-4852-9749-23ab9ff9c6f7'),
        (f'{tenant_name} Go By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=22be2ba4-34df-4cef-afb0-bd74980adab0'),
        (f'{tenant_name} Go',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=5c49a8c7-13e4-4137-b477-3e1386c9bd78'),
        (f'{tenant_name} Hosts (Detailed) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=52406143-afb9-4e38-8d70-c9a0c0d4bcdc'),
        (f'{tenant_name} Hosts (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=ed02d9ac-0b43-4d27-9946-8a817cd01d59'),
        (f'{tenant_name} Hosts By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cdafc693-577f-47a3-a66a-f008626d0b6e'),
        (f'{tenant_name} Hosts',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2bb270ac-cd45-4148-8bb3-78c776febcca'),
        (f'{tenant_name} Java Memory By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8a5d30b1-1426-489f-bad0-59c59c70ffc7'),
        (f'{tenant_name} Java Memory',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=66117e2a-545b-452a-93df-26817074dc84'),
        (f'{tenant_name} Network (Host-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=541d9cd5-0856-4278-aa62-f23cacc84353'),
        (f'{tenant_name} Network (Host-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=fca581fe-6e91-4d37-ac3c-fa62fac48085'),
        (f'{tenant_name} Network (Process-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=88605f16-7d21-4b25-a67d-1d6581a2634e'),
        (f'{tenant_name} Network (Process-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=7a763f8f-bb02-4d8b-8eb8-b2d10b1f2252'),
        (f'{tenant_name} Node.js By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4635787a-ef46-4213-9877-e836820da060'),
        (f'{tenant_name} Node.js',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=89b87451-cf6f-4cf9-ac66-a44c825b303e'),
        (f'{tenant_name} Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=dff7a89a-9209-4333-ba90-4b1da7d67fb2'),
        (f'{tenant_name} Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d92979a1-07e2-45d9-bdce-913d968846ea'),
        (f'{tenant_name} Service Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d478262a-44b7-4882-8f2f-717c8deb9444'),
        (f'{tenant_name} Service Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c6eeaeed-209c-480e-a827-7f4ce059186a'),
        (f'{tenant_name} Service HTTP Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a46a603c-b808-43db-b56c-e76bd8f0afe5'),
        (f'{tenant_name} Service HTTP Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e230801e-7d2e-4845-ab16-eeaed8fe12d9'),
        (f'{tenant_name} Services By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cebf26bb-0cee-456d-9af8-62225e5b42e9'),
        (f'{tenant_name} Services',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a427698e-8125-4aec-9223-b01f6a08b70b'),
        (f'{tenant_name} Synthetics HTTP Monitors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e0c86efb-8cc8-4ed9-a802-6fa507e55f01'),
        (f'{tenant_name} VMware',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2ea1c750-5df7-423c-9bb0-0807154ad646'),
        (f'{tenant_name} Web Servers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=caac1d4e-ecb7-401c-bc52-8ff2343c634f'),
        (f'{tenant_name} Web Servers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=16c6d78e-1aa2-4466-a9c1-a9bdaced7356'),
    ]

    if tenant_name.lower() == 'prod':
        return prod_links
    else:
        print(f'Unsupported tenant name: {tenant_name}')
        exit(1)


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
    ]
    dynatrace_owner = '50436aec-8901-4282-ae81-690bd6509b18'

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
        'Azure Classic',
        'Dashboards',
        'Dashboards Classic',
        'Data Explorer',
        'Databases',
        'Database Services Classic',
        'Distributed Tracing',
        'Distributed Traces Classic',
        'Extensions',
        'Extensions Classic',  # FIXED title to avoid duplication
        'Host Networking',
        'Hosts Classic',
        'Infrastructure & Operations',
        'Launcher',
        'Logs',
        'Multidimensional Analysis',
        'Notebooks',
        'Problems',
        'Problems Classic',
        'Segments',
        'Services',
        'Services Classic',
        'Technologies & Processes Classic',
        'Workflows',
    ]

    app_dict = {}
    filename = 'Launchpads/Assets/Quick Application Links.json'
    with codecs.open(filename, encoding='utf-8') as f:
        document = f.read()
        document_json = json.loads(document)
        block = document_json.get('containerList').get('containers')[0].get('blocks')[0]
        block_content_list = block.get('content')
        if block_content_list:
            for link in block_content_list:
                link_title = link.get('title')
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
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env_name, env, client_id, client_secret)


if __name__ == '__main__':
    main()
