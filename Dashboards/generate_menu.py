import json
import glob

# GENERATED_ID = 'aaaaaaaa-bbbb-cccc-dddd-000000000000'
# GENERATED_NAME = 'Generated Dashboards Menu'
# GENERATED_ID = 'aaaaaaaa-bbbb-cccc-eeee-000000000000'
# GENERATED_NAME = 'Detailed Drilldowns Menu'
# GENERATED_NAME = 'AWS Supporting Services'
# GENERATED_ID = 'aaaaaaaa-bbbb-cccc-0000-000000000000'
# GENERATED_NAME = 'AWS Metrics via CloudWatch Metric Stream'
# GENERATED_ID = 'aaaaaaaa-bbbb-cccc-abcd-000000000000'

GENERATED_PATH = '../$Output/Dashboards/AWSSupportingServices'
GENERATED_ID = 'aaaaaaaa-bbbb-cccc-eeee-f00000000000'
GENERATED_NAME = 'AWS Supporting Services (Improved)'

# path='./????????-????-????-????-????????????.json'
# path='./????????-????-????-????-????????????'
# path = '../$Output/DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-0000-0000000000??.json'
# path = '../$Output/DynatraceDashboardGenerator/aaaaaaaa-bbbb-cccc-abcd-0000000000??.json'
path = '../$Output/Dashboards/AWSSupportingServices/*.json'

dashboard_template_top = '''{
  "metadata": {
    "configurationVersions": [
      5
    ],
    "clusterVersion": "1.251.142.20220929-111511"
  },
  "id": "$$GENERATED_ID$$",
  "dashboardMetadata": {
    "name": "$$GENERATED_NAME$$",
    "shared": true,
    "sharingDetails": {
        "linkShared": true,
        "published": true
    },
    "owner": "nobody@example.com.com"
  },
  "tiles": [
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
        "top": 0,
        "left": 0,
        "width": 2660,
        "height": 3800
      },
      "tileFilter": {},'''

dashboard_template_bottom = '''    }
  ]
}'''

'''
Some Examples of markdown links:
"markdown": "## Manu\n\n[link](https://dynatrace.com)"
"markdown": "#[Overview](#dashboard;id=bbbbbbbb-0001-0000-0000-000000000000)\n#[Executive Overview](#dashboard;gtf=l_24_HOURS;gf=all;id=bbbbbbbb-a004-a017-0000-000000000001)\n#[SRE RUM](#dashboard;gtf=-2h;gf=all;id=bbbbbbbb-a001-a014-0000-000000000002)\n#[SRE Services](#dashboard;gtf=-1h;gf=all;id=bbbbbbbb-a001-a014-0000-000000000003)  \n"
'''

# PROD
# ignore_list = [
#     'Amazon ActiveMQ',
#     'Amazon Athena',
#     'Amazon CloudWatch Logs',
#     # 'Amazon Connect',
#     'Amazon DocumentDB',
#     'Amazon EC2 API',
#     # 'Amazon EC2 Auto Scaling',
#     'Amazon Elastic Kubernetes Service (EKS)',
#     'Amazon Elastic Transcoder',
#     'Amazon EventBridge',
#     'Amazon FSx',
#     'Amazon Gamelift',
#     'Amazon Inspector',
#     'Amazon Keyspaces',
#     # 'Amazon Lex',
#     'Amazon MediaPackage Video on Demand',
#     'Amazon MSK (Kafka)',
#     'Amazon Neptune',
#     'Amazon Polly',
#     'Amazon QLDB',
#     'Amazon RabbitMQ',
#     'Amazon Rekognition',
#     'Amazon Route 53',
#     'Amazon SWF',
#     'Amazon Textract',
#     'Amazon Transit Gateway',
#     'Amazon Translate',
#     'Amazon WAFV2',
#     'Amazon WorkMail',
#     'AWS API Usage',
#     'AWS AppStream 2.0',
#     'AWS AppSync',
#     'AWS Billing',
#     'AWS Chatbot',
#     'AWS CloudHSM',
#     'AWS CloudSearch',
#     'AWS CodeBuild',
#     'AWS DataSync',
#     'AWS Direct Connect',
#     'AWS DMS',
#     'AWS DynamoDB Accelerator (DAX)',
#     # 'AWS ECS ContainerInsights',
#     'AWS Elastic Beanstalk',
#     'AWS Elastic Inference',
#     'AWS Elemental MediaConnect',
#     'AWS IoT Analytics',
#     'AWS IoT Things Graph',
#     'AWS MediaConvert',
#     'AWS OpsWorks',
#     'AWS RoboMaker',
#     'AWS Route 53 Resolver',
#     'AWS Service Catalog',
#     # 'AWS Site-to-Site VPN',
#     'AWS Step Functions',
#     'AWS Storage Gateway',
#     'AWS Systems Manager - Run Command',
#     'AWS Transfer Family',
#     'AWS Trusted Advisor',
#     'AWS WAF Classic',
#     'AWS WorkSpaces',
# ]
# PREP
ignore_list = [
    'Amazon ActiveMQ',
    'Amazon Athena',
    # 'Amazon CloudWatch Logs',
    # 'Amazon Connect',
    'Amazon DocumentDB',
    'Amazon EC2 API',
    # 'Amazon EC2 Auto Scaling',
    'Amazon Elastic Kubernetes Service (EKS)',
    'Amazon Elastic Transcoder',
    # 'Amazon EventBridge',
    'Amazon FSx',
    'Amazon Gamelift',
    'Amazon Inspector',
    'Amazon Keyspaces',
    # 'Amazon Lex',
    'Amazon MediaPackage Video on Demand',
    'Amazon MSK (Kafka)',
    'Amazon Neptune',
    'Amazon Polly',
    'Amazon QLDB',
    'Amazon RabbitMQ',
    'Amazon Rekognition',
    # 'Amazon Route 53',
    'Amazon SWF',
    'Amazon Textract',
    'Amazon Transit Gateway',
    'Amazon Translate',
    'Amazon WAFV2',
    'Amazon WorkMail',
    # 'AWS API Usage',
    'AWS AppStream 2.0',
    'AWS AppSync',
    # 'AWS Billing',
    'AWS Chatbot',
    'AWS CloudHSM',
    'AWS CloudSearch',
    'AWS CodeBuild',
    'AWS DataSync',
    'AWS Direct Connect',
    'AWS DMS',
    # 'AWS DynamoDB Accelerator (DAX)',
    # 'AWS ECS ContainerInsights',
    'AWS Elastic Beanstalk',
    'AWS Elastic Inference',
    'AWS Elemental MediaConnect',
    'AWS IoT Analytics',
    'AWS IoT Things Graph',
    'AWS MediaConvert',
    'AWS OpsWorks',
    'AWS RoboMaker',
    # 'AWS Route 53 Resolver',
    'AWS Service Catalog',
    # 'AWS Site-to-Site VPN',
    'AWS Step Functions',
    # 'AWS Storage Gateway',
    'AWS Systems Manager - Run Command',
    'AWS Transfer Family',
    # 'AWS Trusted Advisor',
    # 'AWS WAF Classic',
    'AWS WorkSpaces',
]
# DEV
# ignore_list = [
#     'Amazon ActiveMQ',
#     'Amazon Athena',
#     'Amazon CloudWatch Logs',
#     'Amazon Connect',
#     'Amazon DocumentDB',
#     'Amazon EC2 API',
#     'Amazon EC2 Auto Scaling',
#     'Amazon Elastic Kubernetes Service (EKS)',
#     'Amazon Elastic Transcoder',
#     'Amazon EventBridge',
#     'Amazon FSx',
#     'Amazon Gamelift',
#     'Amazon Inspector',
#     'Amazon Keyspaces',
#     'Amazon Lex',
#     'Amazon MediaPackage Video on Demand',
#     'Amazon MSK (Kafka)',
#     'Amazon Neptune',
#     'Amazon Polly',
#     'Amazon QLDB',
#     'Amazon RabbitMQ',
#     'Amazon Rekognition',
#     'Amazon Route 53',
#     'Amazon SWF',
#     'Amazon Textract',
#     'Amazon Transit Gateway',
#     'Amazon Translate',
#     'Amazon WAFV2',
#     'Amazon WorkMail',
#     'AWS API Usage',
#     'AWS AppStream 2.0',
#     'AWS AppSync',
#     'AWS Billing',
#     'AWS Chatbot',
#     'AWS CloudHSM',
#     'AWS CloudSearch',
#     'AWS CodeBuild',
#     'AWS DataSync',
#     'AWS Direct Connect',
#     'AWS DMS',
#     'AWS DynamoDB Accelerator (DAX)',
#     'AWS ECS ContainerInsights',
#     'AWS Elastic Beanstalk',
#     'AWS Elastic Inference',
#     'AWS Elemental MediaConnect',
#     'AWS IoT Analytics',
#     'AWS IoT Things Graph',
#     'AWS MediaConvert',
#     'AWS OpsWorks',
#     'AWS RoboMaker',
#     'AWS Route 53 Resolver',
#     'AWS Service Catalog',
#     'AWS Site-to-Site VPN',
#     'AWS Step Functions',
#     'AWS Storage Gateway',
#     'AWS Systems Manager - Run Command',
#     'AWS Transfer Family',
#     'AWS Trusted Advisor',
#     'AWS WAF Classic',
#     'AWS WorkSpaces',
# ]
# ignore_list = ['Generated Dashboards Menu','AWS Supporting Services Menu']

check_list = ['AWS Auto Scaling', 'AWS Cloudfront', 'AWS DAX', 'AWS ECS', 'AWS EFS', 'AWS Logs', 'AWS NAT Gateways', 'AWS Route 53', 'AWS SNS', 'AWS SQS', 'AWS Trusted Advisor', 'AWS Usage', 'AWS VPN']
warn_list = ['AWS API Gateway', 'AWS Container Insights', 'AWS ES', 'AWS Events', 'AWS Kinesis Data Streams', 'AWS SES', 'AWS Storage Gateway', 'AWS WAF']
x_list = ['AWS Athena', 'AWS Aurora', 'AWS DMS', 'AWS DocDB', 'AWS EC2 API', 'AWS EC', 'AWS Glue', 'AWS Kinesis Data Analytics', 'AWS S3', 'AWS SSM Run Command', 'AWS ACM Private CA', 'AWS App Runner', 'AWS App Stream', 'AWS App Sync', 'AWS Billing', 'AWS Cassandra', 'AWS Chatbot', 'AWS Cloud HSM', 'AWS Cloud Search', 'AWS Code Build', 'AWS Connect', 'AWS Data Sync', 'AWS DX', 'AWS Elastic Beanstalk', 'AWS Elastic Inference', 'AWS Elastic Transcoder', 'AWS EMR', 'AWS FSX', 'AWS Gamelift', 'AWS MQ', 'AWS SNS', 'AWS States']

check_emoji = '✅'
warn_emoji = '⚠️'
x_emoji = "❌"

links = ''

top = dashboard_template_top.replace('$$GENERATED_ID$$', GENERATED_ID).replace('$$GENERATED_NAME$$', GENERATED_NAME)
print(top)
for filename in glob.glob(path):
    with open(filename, 'r', encoding='utf-8') as f:
        dashboard = json.loads(f.read())
        dashboard_name = dashboard["dashboardMetadata"]["name"]
        compare_name = dashboard_name[5:]
        # print(compare_name)
        if dashboard_name not in ignore_list:
            if compare_name in check_list:
                dashboard_name = dashboard_name + check_emoji
            if compare_name in warn_list:
                dashboard_name = dashboard_name + warn_emoji
            if compare_name in x_list:
                dashboard_name = dashboard_name + x_emoji
            dashboard_id = dashboard["id"]
            links = links + '[' + dashboard_name + '](#dashboard;id=' + dashboard_id + ')  \\n'
            # print(links)
            # print(dashboard["id"])
            # print(dashboard["dashboardMetadata"]["name"])
            # id = filename.replace(".\\" ,"").replace(".json", "")
            # print(id)
            # md = [link](https://dynatrace.com)
print('"markdown": "' + links + '"')
print(dashboard_template_bottom)

output_file_name = GENERATED_PATH + '/' + GENERATED_ID + '.json'
with open(output_file_name, 'w', encoding='utf-8') as file:
    file.write(top)
    file.write('"markdown": "' + links + '"')
    file.write(dashboard_template_bottom)
