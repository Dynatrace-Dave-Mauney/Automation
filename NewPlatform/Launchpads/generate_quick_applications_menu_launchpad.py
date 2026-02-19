import copy
import json

from Reuse import environment
from Reuse import new_platform_api

include_list = [
    'Anomaly Detection',
    'Azure Classic',
    'Clouds',
    'Dashboards',
    'Dashboards Classic',
    'Data Explorer Classic',
    'Extensions',
    'Host Networking',
    'Hosts Classic',
    'Infrastructure & Operations',
    'Launcher',
    'Logs',
    'Metrics Classic',
    'Notebooks',
    'Problems',
    'Problems Classic',
    'Settings',
    'Settings Classic',
    'Smartscape',
    'Smartscape Classic',
    'Technologies & Processes Classic',
    'User Settings',
    'Workflows',
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
                        "title": "Quick Application Links",
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
    app_links = []
    for application in application_list:
        application_id = application.get('id')
        application_name = application.get('name')
        application_app_icon = application.get('appIcon').get('href')

        app_link = copy.deepcopy(app_link_template)
        app_link['id'] = 'aaaaaaaa-bbbb-cccc-dddd-000000000001'
        app_link['title'] = application_name
        app_link['action']['appId'] = application_id
        app_link['icon'] = application_app_icon

        if application_name in include_list:
            app_links.append(app_link)

    app_link_dict = {}
    for app_link in app_links:
        app_link_dict[app_link.get('title')] = app_link

    keys = sorted(app_link_dict.keys())

    sorted_app_links = []
    for key in keys:
        sorted_app_links.append(app_link_dict[key])

    app_links_launchpad['containerList']['containers'][0]['blocks'][0]['content'] = sorted_app_links

    write_launchpad(app_links_launchpad)


def write_launchpad(launchpad_json):
    with open('Quick Application List.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(launchpad_json, indent=4, sort_keys=False))


def main():
    friendly_function_name = 'Dynatrace Automation'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)

    process(env, client_id, client_secret)


if __name__ == '__main__':
    main()
