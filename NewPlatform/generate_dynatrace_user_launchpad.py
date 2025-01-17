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
    shared_launchpad_blocks.append(generate_documentation_block('Dynatrace User Documentation', get_documentation_links()))
    shared_launchpad_blocks.append(generate_documentation_block('Dynatrace University', get_university_links()))

    write_launchpad(shared_launchpad)


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
    launchpad_block = copy.deepcopy(launchpad_block_template)
    shared_markdown_string = f'#  {block_name}  \n'

    for documentation_link in documentation_links:
        documentation_link_markdown = f'[{documentation_link[0]}]({documentation_link[1]})  \n'
        shared_markdown_string += documentation_link_markdown

    launchpad_block['content'] = shared_markdown_string
    return launchpad_block


def write_launchpad(launchpad_json):
    with open('Dynatrace User Launchpad.json', 'w', encoding='utf-8') as outfile:
        outfile.write(json.dumps(launchpad_json, indent=4, sort_keys=False))


def main():
    process()


if __name__ == '__main__':
    main()
