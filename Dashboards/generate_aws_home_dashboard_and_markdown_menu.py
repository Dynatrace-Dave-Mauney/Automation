"""
Generate "AWS Home Menu" Dashboard JSON.
"""

import json

# directory_path = '../../Dashboards/Templates/Overview'
directory_path = 'Templates/Overview'
dashboard_name = '00000000-dddd-bbbb-ffff-000000001000.json'

def main():
	dashboard_links = [
		('AWS API Usage', '#dashboard;id=bbfc992a-da6d-45ee-be47-df6b217ad765'),
		('AWS DMS', '#dashboard;id=8e25b445-26ea-4812-b805-88df626afbd6'),
		('AWS Step Functions', '#dashboard;id=4387929f-68b1-4d71-a2b1-4e601856ef09'),
		('AWS Systems Manager - Run Command', '#dashboard;id=2907d217-d5ef-480e-9b44-c7b66a8028a8'),
		('AWS Trusted Advisor', '#dashboard;id=a55d8a88-0841-43fd-be97-68f4b877f97b'),
		('AWS WAF Classic', '#dashboard;id=758754a5-8e25-46ec-b970-d4da24424425'),
		('AWS WAFV2', '#dashboard;id=ee0dd7a8-15ca-4b94-af6e-0a37f8361f1a'),
		('Amazon CloudWatch Logs', '#dashboard;id=b8e6ea06-70c3-4bfa-8fef-d3c68c7a7c67'),
		('Amazon EC2 Auto Scaling', '#dashboard;id=7906dd7c-d5b0-4cf5-be45-8228d45d349e'),
		('Amazon EventBridge', '#dashboard;id=0c111823-b2c6-4ee6-98a1-5acba91c8579'),
		('Amazon MSK (Kafka)', '#dashboard;id=a3302849-c910-489b-b12d-547da6652b8f'),
		('AWS API Gateway', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001102'),
		('AWS AZ', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001103'),
		('AWS Aurora', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001104'),
		('AWS Auto Scaling', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001105'),
		('AWS Cloudfront', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001106'),
		('AWS EC', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001107'),
		('AWS ECS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001108'),
		('AWS EFS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001109'),
		('AWS ES', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001110'),
		('AWS Elastic Transcoder', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001111'),
		('AWS Events', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001112'),
		('AWS Kafka 1', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001113'),
		('AWS Kafka 2', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001114'),
		('AWS Kafka 3', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001115'),
		('AWS Kafka 4', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001116'),
		('AWS Lambda', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001117'),
		('AWS Route 53', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001118'),
		('AWS S3', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001119'),
		('AWS SES', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001120'),
		('AWS SNS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001121'),
		('AWS SQS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001122'),
		('AWS SSM Run Command', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001123'),
		('AWS States', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001124'),
		('AWS WAF', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001125'),
	]

	dashboard_links_ootb_only = [
		('AWS API Usage', '#dashboard;id=bbfc992a-da6d-45ee-be47-df6b217ad765'),
		('AWS AppSync', '#dashboard;id=a0ad606f-222b-41ed-9496-2d4537b0131c'),
		('AWS Billing', '#dashboard;id=c12daf08-2a86-4efa-b713-9175b5b4017b'),
		('AWS Chatbot', '#dashboard;id=6603edf1-ac82-408a-ab91-22300392f916'),
		('AWS CloudHSM', '#dashboard;id=2ad079b1-a011-4a97-99f7-e3403ded9320'),
		('AWS CodeBuild', '#dashboard;id=1736b64b-b118-44f6-b8f6-2fc359fefda6'),
		('AWS DMS', '#dashboard;id=8e25b445-26ea-4812-b805-88df626afbd6'),
		('AWS DataSync', '#dashboard;id=2e159e18-84e0-4c7f-9cd9-4f74e0a67ef8'),
		('AWS Direct Connect', '#dashboard;id=b17d6b42-27cd-4dd4-9783-65b302179e79'),
		('AWS Elastic Beanstalk', '#dashboard;id=eb674d20-56c1-4731-9937-111784ea8a77'),
		('AWS Elemental MediaConnect', '#dashboard;id=dd718e88-568d-4169-8bfe-843effa4c5b4'),
		('AWS Elemental MediaConvert', '#dashboard;id=11063ed5-3487-49a6-89de-1e375d9db904'),
		('AWS Elemental MediaPackage Live', '#dashboard;id=de71298c-84a2-4ee9-bfd1-b4bd7b5ed4ef'),
		('AWS Elemental MediaPackage Video on Demand', '#dashboard;id=da982f28-acf3-4dde-843e-f97dcf782910'),
		('AWS IoT Analytics', '#dashboard;id=28fb41e2-aea1-4f40-aa51-901fdbfa53ba'),
		('AWS IoT Things Graph', '#dashboard;id=8cdc638a-f8fe-4a09-b38a-56867ae9c36a'),
		('AWS OpsWorks', '#dashboard;id=57ded21c-cb66-4a96-97c3-b1a8afaf9c7a'),
		('AWS RoboMaker', '#dashboard;id=9b291bad-95dd-4586-a068-a7235e9c65c7'),
		('AWS Service Catalog', '#dashboard;id=4373d0d5-7174-4fd8-88f1-1328898c8b8a'),
		('AWS Site-to-Site VPN', '#dashboard;id=64353676-7e3a-4e30-aff9-cdfc4e2aeac7'),
		('AWS Step Functions', '#dashboard;id=4387929f-68b1-4d71-a2b1-4e601856ef09'),
		('AWS Storage Gateway', '#dashboard;id=09372eaa-3347-4959-a049-3c993fe3420f'),
		('AWS Systems Manager - Run Command', '#dashboard;id=2907d217-d5ef-480e-9b44-c7b66a8028a8'),
		('AWS Transfer Family', '#dashboard;id=ea31d211-6e6c-409e-b077-10b8cdf84a44'),
		('AWS Transit Gateway', '#dashboard;id=7392756f-7e14-4e2e-8a2c-f5b86ea2c5cb'),
		('AWS Trusted Advisor', '#dashboard;id=a55d8a88-0841-43fd-be97-68f4b877f97b'),
		('AWS WAF Classic', '#dashboard;id=758754a5-8e25-46ec-b970-d4da24424425'),
		('AWS WAFV2', '#dashboard;id=ee0dd7a8-15ca-4b94-af6e-0a37f8361f1a'),
		('Amazon ActiveMQ', '#dashboard;id=492fa8c2-427e-430c-8856-7bf32d6be64d'),
		('Amazon AppStream 2.0', '#dashboard;id=142e5d23-564e-4105-bcb7-ef6d2539eb16'),
		('Amazon Athena', '#dashboard;id=99c6d8f1-a355-46bd-9f6a-f2a85f30efcf'),
		('Amazon CloudSearch', '#dashboard;id=3db211a4-7bad-4352-a112-f5b085569b03'),
		('Amazon CloudWatch Logs', '#dashboard;id=b8e6ea06-70c3-4bfa-8fef-d3c68c7a7c67'),
		('Amazon Connect', '#dashboard;id=c82a7373-c954-4b32-a374-fdb0be89de92'),
		('Amazon DocumentDB', '#dashboard;id=f3c583cc-e106-476c-bdd2-25ad94c06c62'),
		('Amazon DynamoDB Accelerator (DAX)', '#dashboard;id=f388375b-a36e-4d18-ba47-0187f43c2446'),
		('Amazon EC2 API', '#dashboard;id=f04f2660-92cd-4110-8551-e2d10e57d48e'),
		('Amazon EC2 Auto Scaling', '#dashboard;id=7906dd7c-d5b0-4cf5-be45-8228d45d349e'),
		('Amazon ECS Container Insights', '#dashboard;id=7645a470-292c-486a-b9cc-b60be94d52f5'),
		('Amazon Elastic Inference', '#dashboard;id=f8602ab8-e9fd-4886-92b1-f554c7d2a77e'),
		('Amazon Elastic Kubernetes Service (EKS)', '#dashboard;id=74e63e2e-a084-482c-a87d-d96e87192c23'),
		('Amazon Elastic Transcoder', '#dashboard;id=f513a269-3c4e-43f5-8af0-87566ff2b669'),
		('Amazon EventBridge', '#dashboard;id=0c111823-b2c6-4ee6-98a1-5acba91c8579'),
		('Amazon FSx', '#dashboard;id=749b26af-a1a9-4e05-8971-3789b1990251'),
		('Amazon Gamelift', '#dashboard;id=d1db4156-2ff5-40ce-814d-484948a72de6'),
		('Amazon Inspector', '#dashboard;id=221fc341-ffca-44b0-976e-0231626ffbd3'),
		('Amazon Keyspaces', '#dashboard;id=d1d89988-8125-4f0f-b6e1-f5a85d781f3a'),
		('Amazon Lex', '#dashboard;id=f3d22b91-e261-4251-be93-a0636f7fc634'),
		('Amazon MSK (Kafka)', '#dashboard;id=a3302849-c910-489b-b12d-547da6652b8f'),
		('Amazon Neptune', '#dashboard;id=de1f11bf-4b1e-40f1-b397-c5c8688bfb65'),
		('Amazon Polly', '#dashboard;id=6097a165-9365-4ca8-bcd5-1c593c690c19'),
		('Amazon QLDB', '#dashboard;id=9eb37cea-591e-474b-8cf5-89006cddb239'),
		('Amazon RabbitMQ', '#dashboard;id=4ae9a988-46b1-4d61-81c8-ea58859b9c23'),
		('Amazon Rekognition', '#dashboard;id=81384f19-c297-48d8-9195-b72252f72907'),
		('Amazon Route 53 Resolver', '#dashboard;id=6a8972fc-ffdc-426d-b0e8-86af68049cc4'),
		('Amazon Route 53', '#dashboard;id=454c4321-e972-401d-847d-53c421c76fcb'),
		('Amazon SWF', '#dashboard;id=26d06109-347c-4c7d-b7f7-a293e0a4f201'),
		('Amazon Textract', '#dashboard;id=3bd5a934-bd30-4513-8097-04be12ba4b99'),
		('Amazon Translate', '#dashboard;id=6096e827-de96-4302-aaf6-6327a3bfdf86'),
		('Amazon WorkMail', '#dashboard;id=18968e11-c857-4592-9913-b99e0109a848'),
		('Amazon WorkSpaces', '#dashboard;id=a0598f11-1cd1-4594-810e-c1251d3b6178'),
	]

	dashboard_links_generated_only = [
		('AWS ALB', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001023'),
		('AWS API Gateway', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001008'),
		('AWS CloudWatch Logs', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001010'),
		('AWS Cloudfront', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001009'),
		('AWS Connect', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001011'),
		('AWS Connect Details', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001020'),
		('AWS DynamoDB', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001002'),
		('AWS DynamoDB Accelerator (DAX)', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001022'),
		('AWS EBS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001003'),
		('AWS EC2', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001004'),
		('AWS EC2 Auto Scaling', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001021'),
		('AWS ECS ContainerInsights', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001013'),
		('AWS ECS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001012'),
		('AWS ES', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001024'),
		('AWS Kinesis Data Streams', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001019'),
		('AWS Lambda Functions', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001005'),
		('AWS Lex', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001014'),
		('AWS NAT Gateways', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001015'),
		('AWS NLB', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001006'),
		('AWS RDS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001007'),
		('AWS Route 53', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001016'),
		('AWS Route 53 Resolver', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001017'),
		('AWS Site-to-Site VPN', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001018'),
		('AWS SQS', '#dashboard;id=00000000-dddd-bbbb-ffff-000000001025'),
	]

	view_links = [
		('AWS', '#awses'),
		('AWS Settings', '#settings/awsmonitoring'),
	]

	drilldown_title = '## {{.title}}  \\n'

	dashboard_template = '''{
  "metadata": {
    "configurationVersions": [
      6
    ],
    "clusterVersion": "1.261.134.20230302-084304"
  },
  "id": "00000000-dddd-bbbb-ffff-000000001000",
  "dashboardMetadata": {
    "name": "TEMPLATE: AWS Home",
    "shared": true,
    "owner": "nobody@example.com",
    "preset": false,
    "tilesNameSize": "small",
    "hasConsistentColors": true
  },
  "tiles": [
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
        "top": 0,
        "left": 0,
        "width": 494,
        "height": 2888
      },
      "tileFilter": {},
      "isAutoRefreshDisabled": false,
	  "markdown": "{{.dashboard_markdown}}"
    },
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
        "top": 0,
        "left": 494,
        "width": 494,
        "height": 2888
      },
      "tileFilter": {},
      "isAutoRefreshDisabled": false,
	  "markdown": "{{.view_markdown}}"
    },
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
          "top": 0,
          "left": 1368,
          "width": 152,
          "height": 38
      },
      "tileFilter": {},
      "markdown": "#### [\u21e6 Overview](#dashboard;id=00000000-dddd-bbbb-ffff-000000000001)\\n![BackButton]()"
    }
  ]
}
	'''

	dashboard_markdown_title = drilldown_title.replace('{{.title}}', 'Dashboards')
	dashboard_markdown = dashboard_markdown_title
	for dashboard_link in dashboard_links:
		dashboard_key, dashboard_link = dashboard_link
		dashboard_markdown += f'  \\n[{dashboard_key}]({dashboard_link})'

	view_markdown_title = drilldown_title.replace('{{.title}}', 'Views')
	view_markdown = view_markdown_title
	for view_link in view_links:
		view_key, view_link = view_link
		view_markdown += f'  \\n[{view_key}]({view_link})'

	dashboard_template = dashboard_template.replace('{{.dashboard_markdown}}', dashboard_markdown)
	dashboard_template = dashboard_template.replace('{{.view_markdown}}', view_markdown)

	print(dashboard_template)

	write_json(directory_path, dashboard_name, json.loads(dashboard_template))

	aws_markdown_menu = '			"markdown": "'
	for dashboard_link in dashboard_links:
		dashboard_key, dashboard_link = dashboard_link
		aws_markdown_menu += f'  \\n[{dashboard_key}]({dashboard_link})'
	aws_markdown_menu += '"'

	filename = 'Templates/Overview/markdown_aws_menu.json'
	with open(filename, 'w') as file:
		file.write(aws_markdown_menu)



def write_json(directory_path, filename, json_dict):
	# print('write_json(' + directory_path + ',' + filename + ',' + str(json_dict) + ')')
	file_path = f'{directory_path}/{filename}'
	print(f'Generated: {file_path}')
	with open(file_path, 'w', encoding='utf-8') as file:
		file.write(json.dumps(json_dict, indent=4, sort_keys=False))


if __name__ == '__main__':
	main()
