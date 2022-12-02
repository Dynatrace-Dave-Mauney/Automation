#
# For each Dynatrace AWS Supporting Service dashboard:
#
# 1. Convert owner
# 2. Convert dashboard ID
#

import copy
import glob
import json
import os

OWNER = os.environ.get('DASHBOARD_OWNER_EMAIL', 'nobody@example.com')

DASHBOARD_INPUT_PATH = '../$Test/Dashboards/DataExplorer/AWSSupportingServices'
DASHBOARD_OUTPUT_PATH = '../$Test/Dashboards/AWSSupportingServices'

dashboard_name_to_id = {
    'Amazon ActiveMQ': 'aaaaaaaa-bbbb-cccc-eeee-f00000000001',
    'Amazon Athena': 'aaaaaaaa-bbbb-cccc-eeee-f00000000002',
    'Amazon CloudWatch Logs': 'aaaaaaaa-bbbb-cccc-eeee-f00000000003',
    'Amazon Connect': 'aaaaaaaa-bbbb-cccc-eeee-f00000000004',
    'Amazon DocumentDB': 'aaaaaaaa-bbbb-cccc-eeee-f00000000005',
    'Amazon EC2 API': 'aaaaaaaa-bbbb-cccc-eeee-f00000000006',
    'Amazon EC2 Auto Scaling': 'aaaaaaaa-bbbb-cccc-eeee-f00000000007',
    'Amazon Elastic Kubernetes Service (EKS)': 'aaaaaaaa-bbbb-cccc-eeee-f00000000008',
    'Amazon Elastic Transcoder': 'aaaaaaaa-bbbb-cccc-eeee-f00000000009',
    'Amazon EventBridge': 'aaaaaaaa-bbbb-cccc-eeee-f00000000010',
    'Amazon FSx': 'aaaaaaaa-bbbb-cccc-eeee-f00000000011',
    'Amazon Gamelift': 'aaaaaaaa-bbbb-cccc-eeee-f00000000012',
    'Amazon Inspector': 'aaaaaaaa-bbbb-cccc-eeee-f00000000013',
    'Amazon Keyspaces': 'aaaaaaaa-bbbb-cccc-eeee-f00000000014',
    'Amazon Lex': 'aaaaaaaa-bbbb-cccc-eeee-f00000000015',
    'Amazon MSK (Kafka)': 'aaaaaaaa-bbbb-cccc-eeee-f00000000016',
    'Amazon MediaPackage Live': 'aaaaaaaa-bbbb-cccc-eeee-f00000000017',
    'Amazon MediaPackage Video on Demand': 'aaaaaaaa-bbbb-cccc-eeee-f00000000018',
    'Amazon Neptune': 'aaaaaaaa-bbbb-cccc-eeee-f00000000019',
    'Amazon Polly': 'aaaaaaaa-bbbb-cccc-eeee-f00000000020',
    'Amazon QLDB': 'aaaaaaaa-bbbb-cccc-eeee-f00000000021',
    'Amazon RabbitMQ': 'aaaaaaaa-bbbb-cccc-eeee-f00000000022',
    'Amazon Rekognition': 'aaaaaaaa-bbbb-cccc-eeee-f00000000023',
    'Amazon Route 53': 'aaaaaaaa-bbbb-cccc-eeee-f00000000024',
    'Amazon SWF': 'aaaaaaaa-bbbb-cccc-eeee-f00000000025',
    'Amazon Textract': 'aaaaaaaa-bbbb-cccc-eeee-f00000000026',
    'Amazon Transit Gateway': 'aaaaaaaa-bbbb-cccc-eeee-f00000000027',
    'Amazon Translate': 'aaaaaaaa-bbbb-cccc-eeee-f00000000028',
    'Amazon WAFV2': 'aaaaaaaa-bbbb-cccc-eeee-f00000000029',
    'Amazon WorkMail': 'aaaaaaaa-bbbb-cccc-eeee-f00000000030',
    'AWS API Usage': 'aaaaaaaa-bbbb-cccc-eeee-f00000000031',
    'AWS AppStream 2.0': 'aaaaaaaa-bbbb-cccc-eeee-f00000000032',
    'AWS AppSync': 'aaaaaaaa-bbbb-cccc-eeee-f00000000033',
    'AWS Billing': 'aaaaaaaa-bbbb-cccc-eeee-f00000000034',
    'AWS Chatbot': 'aaaaaaaa-bbbb-cccc-eeee-f00000000035',
    'AWS CloudHSM': 'aaaaaaaa-bbbb-cccc-eeee-f00000000036',
    'AWS CloudSearch': 'aaaaaaaa-bbbb-cccc-eeee-f00000000037',
    'AWS CodeBuild': 'aaaaaaaa-bbbb-cccc-eeee-f00000000038',
    'AWS DMS': 'aaaaaaaa-bbbb-cccc-eeee-f00000000039',
    'AWS DataSync': 'aaaaaaaa-bbbb-cccc-eeee-f00000000040',
    'AWS Direct Connect': 'aaaaaaaa-bbbb-cccc-eeee-f00000000041',
    'AWS DynamoDB Accelerator (DAX)': 'aaaaaaaa-bbbb-cccc-eeee-f00000000042',
    'AWS ECS ContainerInsights': 'aaaaaaaa-bbbb-cccc-eeee-f00000000043',
    'AWS Elastic Beanstalk': 'aaaaaaaa-bbbb-cccc-eeee-f00000000044',
    'AWS Elastic Inference': 'aaaaaaaa-bbbb-cccc-eeee-f00000000045',
    'AWS Elemental MediaConnect': 'aaaaaaaa-bbbb-cccc-eeee-f00000000046',
    'AWS IoT Analytics': 'aaaaaaaa-bbbb-cccc-eeee-f00000000047',
    'AWS IoT Things Graph': 'aaaaaaaa-bbbb-cccc-eeee-f00000000048',
    'AWS MediaConvert': 'aaaaaaaa-bbbb-cccc-eeee-f00000000049',
    'AWS OpsWorks': 'aaaaaaaa-bbbb-cccc-eeee-f00000000050',
    'AWS RoboMaker': 'aaaaaaaa-bbbb-cccc-eeee-f00000000051',
    'AWS Route 53 Resolver': 'aaaaaaaa-bbbb-cccc-eeee-f00000000052',
    'AWS Service Catalog': 'aaaaaaaa-bbbb-cccc-eeee-f00000000053',
    'AWS Site-to-Site VPN': 'aaaaaaaa-bbbb-cccc-eeee-f00000000054',
    'AWS Step Functions': 'aaaaaaaa-bbbb-cccc-eeee-f00000000055',
    'AWS Storage Gateway': 'aaaaaaaa-bbbb-cccc-eeee-f00000000056',
    'AWS Systems Manager - Run Command': 'aaaaaaaa-bbbb-cccc-eeee-f00000000057',
    'AWS Transfer Family': 'aaaaaaaa-bbbb-cccc-eeee-f00000000058',
    'AWS Trusted Advisor': 'aaaaaaaa-bbbb-cccc-eeee-f00000000059',
    'AWS WAF Classic': 'aaaaaaaa-bbbb-cccc-eeee-f00000000060',
    'AWS WorkSpaces': 'aaaaaaaa-bbbb-cccc-eeee-f00000000061',
}


def customize_dashboards():
    for filename in glob.glob(DASHBOARD_INPUT_PATH + '/*'):
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            new_dashboard = customize_dashboard(dashboard)
            pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
            dashboard_name = new_dashboard.get('dashboardMetadata').get('name')
            output_filename = DASHBOARD_OUTPUT_PATH + '/' + dashboard_name + '.json'
            with open(output_filename, 'w') as outfile:
                outfile.write(pretty_new_dashboard)


def customize_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    name = dashboard_json.get('dashboardMetadata').get('name')
    dashboard_id = dashboard_name_to_id.get(name)
    if not dashboard_id:
        print('No id found for', name)
        exit(1)

    new_dashboard_json['id'] = dashboard_id
    new_dashboard_json['dashboardMetadata']['owner'] = OWNER
    return new_dashboard_json


def main():
    customize_dashboards()


if __name__ == '__main__':
    main()
