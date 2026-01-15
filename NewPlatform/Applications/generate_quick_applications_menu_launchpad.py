import copy
import json

from Reuse import environment
from Reuse import new_platform_api

skip_list = [
    'AWS Classic',
    'AWS Connector',
    'AWS',
    'Access Tokens',
    'Agentless Real User Monitoring',  # Customer-specific choice
    'App Shell',
    # 'Azure Classic',
    # 'Azure',
    'Cloud Foundry',  # Customer-specific choice
    # 'Clouds',
    'Cluster DevTools',
    # 'Containers',
    'Credential Vault',
    'Custom Applications',  # Customer-specific choice
    # 'Dashboards Classic',
    # 'Dashboards',
    # 'Data Explorer',
    # 'Database Services Classic',
    # 'Databases',
    # 'Davis Anomaly Detection',
    # 'Davis CoPilot',
    'Deploy ActiveGate',
    'Deploy OneAgent',
    'Deployment Status',
    'Discovery & Coverage',
    # 'Distributed Traces Classic',
    # 'Distributed Tracing',
    'EdgeConnect Management',
    'Email',
    'Explore Business Events',
    'Extensions',
    'Extensions',
    # 'Frontend',  # Customer-specific choice
    'GCP Classic',
    'GitHub',
    'GitLab',
    # 'Host Networking',
    # 'Hosts Classic',
    # 'Hub',
    # 'Infrastructure & Operations',
    'Jenkins',
    'Jira',
    # 'Kubernetes Classic',
    # 'Kubernetes Workloads Classic',
    # 'Kubernetes',
    # 'Launcher',
    # 'Learn DQL',
    'Logs & Events Classic',
    # 'Logs',
    # 'Message Queues',
    # 'Metrics',
    'Microsoft 365',
    'Microsoft Teams',
    'Mobile',  # Customer-specific choice
    # 'Multidimensional Analysis',
    # 'Notebooks',
    'OneAgent Health',
    'OpenPipeline',
    'Ownership',
    'PaaS Integration',
    'PagerDuty',
    'Personal Access Tokens',
    # 'Problems Classic',
    # 'Problems',
    # 'Profiling & Optimization',
    # 'Query User Sessions',
    'Red Hat Ansible',
    'Releases',  # Customer-specific choice
    'Security Investigator',  # Customer-specific choice
    # 'Segments',
    'Service-Level Objectives Classic',
    'Service-Level Objectives',
    'ServiceNow',
    # 'Services Classic',
    # 'Services',
    # 'Session Replay Classic',
    # 'Session Segmentation',
    'Settings Classic',
    'Settings',
    'Site Reliability Guardian',
    'Slack',
    # 'Smartscape Topology',
    'Storage Management',
    # 'Synthetic Classic',
    # 'Synthetic',
    'System Notifications',
    # 'Technologies & Processes Classic',
    'User Settings',
    'VMware Classic',
    'Vulnerabilities',  # Customer-specific choice
    # 'Web',
    # 'Workflows',
    'Attacks',
    'Code-Level Vulnerabilities',
    'Live Debugger',
    'Outbound connections',
    'Text Processing',
    'Third-Party Vulnerabilities',
    'Threats & Exploits',
]

template = {
    "schemaVersion": 2,
    "icon": "default",
    "background": "default",
    "containerList": {
        "containers": [
            {
                "blocks": [
                    {
                        "id": "aaaaaaaa-bbbb-cccc-dddd-000000000000",
                        "type": "links",
                        "properties": {
                            "expanded": True
                        },
                        "appearance": "tile",
                        "title": "Full Application Links",
                        "description": "",
                        "contentType": "static",
                        "content": [
                            {
                                "id": "aaaaaaaa-bbbb-cccc-dddd-000000000000",
                                "type": "app",
                                "title": "Launcher",
                                "action": {
                                    "type": "openApp",
                                    "appId": "dynatrace.launcher"
                                },
                                "icon": "/platform/app-engine/registry/v1/app-icons/dynatrace.launcher?appVersion=2.12.0",
                                "categoryId": "apps"
                            }
                        ]
                    }
                ],
                "horizontalLayoutWeight": 1
            }
        ]
    }
}


def process(env, client_id, client_secret):
    scope = 'app-engine:apps:run'

    app_links_launchpad = copy.deepcopy(template)

    app_link_template = copy.deepcopy(template.get('containerList').get('containers')[0].get('blocks')[0].get('content')[0])

    oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
    params = {'page-size': 1000}
    results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/app-engine/registry/v1/apps', params)
    applications_json = json.loads(results.text)
    application_list = applications_json.get('apps')
    # print(applications_json)
    headers = [['Name', 'ID', 'Version', 'Description', 'Resource Status', 'App Icon', 'Signed', 'Publisher', 'Created By', 'Last Modified By', 'Last Modified At']]
    rows = []
    app_links = []
    for application in application_list:
        application_id = application.get('id')
        application_name = application.get('name')
        application_version = application.get('version')
        application_description = application.get('description')
        application_resourceStatus = application.get('resourceStatus').get('status')
        application_appIcon = application.get('appIcon').get('href')
        application_signatureInfo_signed = application.get('signatureInfo').get('signed')
        application_signatureInfo_publisher = application.get('signatureInfo').get('publisher')
        application_modificationInfo = application.get('modificationInfo')
        application_modificationInfo_createdBy = application_modificationInfo.get('createdBy')
        application_modificationInfo_lastModifiedBy = application_modificationInfo.get('lastModifiedBy')
        application_modificationInfo_lastModifiedAt = application_modificationInfo.get('lastModifiedAt')
        # rows.append([application_name, application_id, application_version, application_description, application_resourceStatus, application_appIcon, application_signatureInfo_signed, application_signatureInfo_publisher, application_modificationInfo_createdBy, application_modificationInfo_lastModifiedBy, application_modificationInfo_lastModifiedAt])

        app_link = copy.deepcopy(app_link_template)
        app_link['id'] = 'aaaaaaaa-bbbb-cccc-dddd-000000000001'
        app_link['title'] = application_name
        app_link['action']['appId'] = application_id
        app_link['icon'] = application_appIcon

        # print(application_name)
        if application_name not in skip_list:
            app_links.append(app_link)
            # print(application_name)

    app_link_dict = {}
    for app_link in app_links:
        app_link_dict[app_link.get('title')] = app_link

    keys = sorted(app_link_dict.keys())
    # print('keys:', keys)

    sorted_app_links = []
    for key in keys:
        # print(key)
        sorted_app_links.append(app_link_dict[key])

    # for sorted_app_link in sorted_app_links:
    #     print(sorted_app_link)

    app_links_launchpad['containerList']['containers'][0]['blocks'][0]['content'] = sorted_app_links
    print(json.dumps(app_links_launchpad))



def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Sandbox'
    #
    # env_name_supplied = 'Upper'
    # env_name_supplied = 'Lower'
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
