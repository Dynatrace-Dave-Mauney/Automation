import copy
import json

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

launchpad_block_template = {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "type": "markdown",
    "properties": {
        "expanded": True
    },
    "content": ""
}


def process():
    shared_launchpad = launchpad_template
    shared_launchpad_blocks = shared_launchpad['containerList']['containers'][0]['blocks']
    shared_launchpad_blocks.append(generate_documentation_block('ActiveGates', get_active_gate_links()))
    shared_launchpad_blocks.append(generate_documentation_block('OneAgents', get_one_agent_links()))
    shared_launchpad_blocks.append(generate_documentation_block('Configuration and Operation', get_configuration_links()))
    shared_launchpad_blocks.append(generate_documentation_block('APIs', get_api_links()))
    shared_launchpad_blocks.append(generate_documentation_block('Tokens/Oauth', get_token_links()))
    shared_launchpad_blocks.append(generate_documentation_block('Security', get_security_links()))

    write_launchpad(shared_launchpad)


def get_active_gate_links():
    links = [
        ('Dynatrace ActiveGate', 'https://docs.dynatrace.com/docs/shortlink/activegate-landing'),
        ('ActiveGate group', 'https://docs.dynatrace.com/docs/shortlink/activegate-group'),
        ('Configuration properties and parameters of ActiveGate', 'https://docs.dynatrace.com/docs/shortlink/sgw-configure'),
        ('Custom SSL certificate for ActiveGate', 'https://docs.dynatrace.com/docs/shortlink/activegate-configuration-ssl'),
        ('Proxy for ActiveGate', 'https://docs.dynatrace.com/docs/shortlink/sgw-proxy-authentication'),
        ('Reverse proxy or load balancer for ActiveGate', 'https://docs.dynatrace.com/docs/shortlink/activegate-reverse-proxy'),
    ]

    return links


def get_one_agent_links():
    links = [
        ('Dynatrace OneAgent', 'https://docs.dynatrace.com/docs/shortlink/oneagent-hub'),
        ('Install OneAgent on Linux', 'https://docs.dynatrace.com/docs/shortlink/oneagent-linux-install'),
        ('Update OneAgent on Linux', 'https://docs.dynatrace.com/docs/shortlink/oneagent-update-linux'),
        ('Stop/restart OneAgent on Linux', 'https://docs.dynatrace.com/docs/shortlink/stop-restart-oneagent-linux'),
        ('Uninstall OneAgent on Linux', 'https://docs.dynatrace.com/docs/shortlink/oneagent-uninstall-linux'),
        ('Install OneAgent on Windows', 'https://docs.dynatrace.com/docs/shortlink/oneagent-windows-install'),
        ('Update Dynatrace OneAgent on Windows', 'https://docs.dynatrace.com/docs/shortlink/oneagent-update-windows'),
        ('Stop/restart OneAgent on Windows', 'https://docs.dynatrace.com/docs/shortlink/stop-restart-oneagent-windows'),
        ('Uninstall Dynatrace OneAgent on Windows', 'https://docs.dynatrace.com/docs/shortlink/oneagent-uninstall-windows'),
        ('OneAgent security', 'https://docs.dynatrace.com/docs/shortlink/oneagent-security'),
        ('OneAgent configuration via command-line interface', 'https://docs.dynatrace.com/docs/shortlink/oneagentctl'),
        ('OneAgent troubleshooting', 'https://docs.dynatrace.com/docs/shortlink/oneagent-troubleshooting'),
        ('OneAgent platform and capability support matrix', 'https://docs.dynatrace.com/docs/shortlink/oneagent-support-matrix'),
    ]

    return links


def get_token_links():
    links = [
        ('Dynatrace API - Tokens and authentication', 'https://docs.dynatrace.com/docs/shortlink/api-authentication'),
        ('Platform tokens', 'https://docs.dynatrace.com/docs/shortlink/platform-tokens'),
        ('Tenant token classic', 'https://docs.dynatrace.com/docs/shortlink/tenant-token'),
        ('OAuth clients', 'https://docs.dynatrace.com/docs/shortlink/oauth'),
    ]

    return links


def get_api_links():
    links = [
        ('Dynatrace API', 'https://docs.dynatrace.com/docs/shortlink/section-api'),
        ('Environment API', 'https://docs.dynatrace.com/docs/shortlink/env-api'),
        ('Configuration API', 'https://docs.dynatrace.com/docs/shortlink/config-api'),
        ('Account Management API', 'https://docs.dynatrace.com/docs/shortlink/account-api'),
        ('API for Dashboards and Notebooks', 'https://docs.dynatrace.com/docs/shortlink/document-api'),
        ('OneAgent metric API', 'https://docs.dynatrace.com/docs/shortlink/local-api'),
        ('Remote configuration management API', 'https://docs.dynatrace.com/docs/shortlink/api-v2-remote-configuration'),
    ]

    return links


def get_security_links():
    links = [
        ('Data privacy and security', 'https://docs.dynatrace.com/docs/shortlink/section-data-privacy-and-security'),
        ('Dynatrace CVE status (Common Vulnerabilities and Exposures)', 'https://community.dynatrace.com/t5/Heads-up-from-Dynatrace/Dynatrace-CVE-status-Common-Vulnerabilities-and-Exposures/ta-p/214793'),
        ('Report a security-related concern', 'https://docs.dynatrace.com/docs/shortlink/who-to-contact-security'),
        ('Trust Center', 'https://www.dynatrace.com/news/tag/trust-center/'),
    ]

    return links


def get_configuration_links():
    links = [
        ('Network zones', 'https://docs.dynatrace.com/docs/shortlink/network-zones'),
        ('Organize your environment using host groups', 'https://docs.dynatrace.com/docs/shortlink/host-groups'),
        ('Tags and metadata', 'https://docs.dynatrace.com/docs/shortlink/tags-and-metadata-hub'),
        ('Management zones', 'https://docs.dynatrace.com/docs/shortlink/management-zones-hub'),
        ('Segments', 'https://docs.dynatrace.com/docs/shortlink/segments'),
        ('Credential vault', 'https://docs.dynatrace.com/docs/shortlink/credential-vault'),
        ('Identity and access management', 'https://docs.dynatrace.com/docs/shortlink/identity-access-management'),
        ('Account Management', 'https://docs.dynatrace.com/docs/shortlink/account-management'),
        ('Permission management', 'https://docs.dynatrace.com/docs/shortlink/permission-management'),
        ('OpenTelemetry and Dynatrace', 'https://docs.dynatrace.com/docs/shortlink/opentelemetry'),
        ('Extensions', 'https://docs.dynatrace.com/docs/shortlink/extensions20'),
        ('Remote configuration management of OneAgents and ActiveGates', 'https://docs.dynatrace.com/docs/shortlink/remote-configuration'),
        ('', ''),
    ]

    return links


# def get_university_links():
#     links = [
#         ('Beginner Level', 'https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=beginner'),
#         ('Intermediate Level', 'https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=intermediate'),
#         ('Advanced Level', 'https://university.dynatrace.com/ondemand?content=dynatrace&skillLevel=advanced'),
#     ]
#
#     return links


def generate_documentation_block(block_name, documentation_links):
    launchpad_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = f'#  {block_name}  \n'

    for documentation_link in documentation_links:
        documentation_link_markdown = f'[{documentation_link[0]}]({documentation_link[1]})  \n'
        shared_markdown_string += documentation_link_markdown

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def write_launchpad(launchpad_json):
    with open('Dynatrace Architecture Launchpad.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(launchpad_json, indent=4, sort_keys=False))


def main():
    process()


if __name__ == '__main__':
    main()
