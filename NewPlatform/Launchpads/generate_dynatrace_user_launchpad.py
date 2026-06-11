import codecs
import copy
import json
import re

from Reuse import environment
from Reuse import new_platform_api

id_index = 1

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
    shared_launchpad_blocks.append(generate_markdown_block('Custom Dashboards', get_dashboard_links(tenant_name, tenant)))
    # shared_launchpad_blocks.append(generate_markdown_block('Custom Dashboards by Management Zone', get_dashboard_links_by_management_zone(tenant_name, tenant)))
    shared_launchpad_blocks.append(generate_markdown_block('Dynatrace User Documentation', get_links()))
    shared_launchpad_blocks.append(generate_markdown_block('Dynatrace University', get_university_links()))
    write_launchpad(shared_launchpad)


def get_dashboard_links(tenant_name, tenant):

    # Use add_environment_shares.py and generate_shared_document_links.py
    # to generate these lists

    prod_links = [
        (f'{tenant_name}: Overview (Classic Dashboard)',
         f'https://{tenant}.live.dynatrace.com/#dashboard;id=00000000-dddd-bbbb-ffff-000000000001'),
        (f'{tenant_name} .NET Monitoring',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/2b512c68-0203-46e9-bab8-4d2368ceaf80'),
        (f'{tenant_name} AWS API Usage',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/4a3812f6-7c78-425f-a46c-8c3f70d731bb'),
        (f'{tenant_name} AWS AZ',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/14b83235-0a15-4bbc-9294-2079bec90183'),
        (f'{tenant_name} AWS Aurora',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/9a6daed5-e984-4a48-befe-dbc18ed61278'),
        (f'{tenant_name} AWS Cloudfront',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/5d4ae555-a71e-42ba-8cb9-82e4c4fee2f8'),
        (f'{tenant_name} AWS EC',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/dd70c585-e6f9-4c21-9b50-e9e0cb7ad0f8'),
        (f'{tenant_name} AWS ECS',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/adbfae2d-5ee1-4cf8-966b-1bf9e802a21a'),
        (f'{tenant_name} AWS EFS',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/95358ede-5e9a-4333-836a-5b453619acc0'),
        (f'{tenant_name} AWS ES',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/b7225a49-51e2-487e-8b72-5bb86e01c2ad'),
        (f'{tenant_name} AWS Events',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/df5812ae-8272-4077-9894-6c6e7173cbe3'),
        (f'{tenant_name} AWS Kafka',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/dcb49c9e-2311-4980-8b59-d52f7d641dd8'),
        (f'{tenant_name} AWS Lambda',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/a969ece5-745c-42e8-bdd7-8a992a73ffc7'),
        (f'{tenant_name} AWS Route 53',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/a1ccdddb-9f4d-4648-a60b-bd181bda9c32'),
        (f'{tenant_name} AWS S3',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/736b7225-b8dc-49f3-a094-0d55e1053376'),
        (f'{tenant_name} AWS SNS',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/4b9f318e-95f1-45da-8523-86b8006e8089'),
        (f'{tenant_name} AWS SQS',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/93affb9d-d61d-4748-9093-f77a664a639b'),
        (f'{tenant_name} AWS WAF',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/7cbac8bc-a806-4a7d-83b7-e4861e72a400'),
        (f'{tenant_name} Backend Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f06decd8-b9bb-46ed-af5c-980cf9a71462'),
        (f'{tenant_name} Backend Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/b1cb4049-343a-4948-884a-055de4f102d1'),
        (f'{tenant_name} Containers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/3341808b-0cdc-4040-99fd-9a12c5a1c497'),
        (f'{tenant_name} Containers',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f72301b5-16f0-4937-80da-80220016bd8d'),
        (f'{tenant_name} Coverage by CMDBID',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/1946d8bc-0690-4830-a43e-bda66d3e3ab6'),
        (f'{tenant_name} Databases',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/2564b125-dee0-48e8-be61-2191e6a670ea'),
        (f'{tenant_name} Full Stack Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/95e8aba3-73e6-40ff-9dd1-451fb9c6d968'),
        (f'{tenant_name} Full Stack Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/ac198ae8-bcd6-4e57-9edc-9cb13fe34bec'),
        (f'{tenant_name} Go By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f30cce0a-dbde-4edf-8682-4810728606d1'),
        (f'{tenant_name} Go',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f6edd29f-785f-4443-a167-ff13db5be6d4'),
        (f'{tenant_name} Hosts (Detailed) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/ea3aceef-395c-4e92-9a46-4426efa8375e'),
        (f'{tenant_name} Hosts (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/c31f2e3c-cfa2-4ef8-acd2-71bd1a1347d1'),
        (f'{tenant_name} Hosts By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/48ffd61e-3c95-4be6-9c07-f0828e098a07'),
        (f'{tenant_name} Hosts',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/84a6068e-e74c-4d6c-a16a-6871bfbeb70d'),
        (f'{tenant_name} IBM MQ Channel',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/cdffd3ce-c682-4783-b643-934dd6018fc7'),
        (f'{tenant_name} IBM MQ Queue',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/254ad67b-bcc2-4b15-b418-482d3bcf6e03'),
        (f'{tenant_name} IBM MQ Topic-Listener-Function',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/1af83f6c-2cf0-4b99-86b1-76afd0415557'),
        (f'{tenant_name} IBM WebSphere Metrics by Pool',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/0bf02c7e-9d89-463c-9551-473ae541f393'),
        (f'{tenant_name} IBM WebSphere Metrics by Process',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/a2d3a8f9-c513-491d-a346-6601d2da6454'),
        (f'{tenant_name} Java Memory By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/b5dabbc0-3a43-4c1b-b985-3de474f71da6'),
        (f'{tenant_name} Java Memory',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/28ce8409-a660-4b9e-9e7d-7f7ba3403b24'),
        (f'{tenant_name} Java Monitoring',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/a130ecf6-e497-40da-859b-3e13d2d91e92'),
        (f'{tenant_name} Key Requests',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/89da3ec0-bdc2-4624-b8c1-31989bf145e2'),
        (f'{tenant_name} Netscaler 1',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/e6473403-5433-4e27-9aad-ab142eb9a636'),
        (f'{tenant_name} Netscaler 2',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/cac2e070-0d25-4661-92f0-6b41efd1a93d'),
        (f'{tenant_name} Network (Host-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/10be41d3-b111-4873-8f4b-ddc18936c923'),
        (f'{tenant_name} Network (Host-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/70a9d424-86ff-4879-bc67-587aefc55133'),
        (f'{tenant_name} Network (Process-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/d426ff53-9c75-45d3-8f0a-d903c0a9a249'),
        (f'{tenant_name} Network (Process-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/b2e07431-2fa3-4dca-8501-0ddf08d5d852'),
        (f'{tenant_name} Node.js By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/50dec2a8-bc94-49b4-b50b-58dc2af57d97'),
        (f'{tenant_name} Node.js',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/4ca40110-d210-4dd7-91b7-3c902992d5ab'),
        (f'{tenant_name} Oracle',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/cf931ef4-7e17-48a0-83d6-68218fc71312'),
        # (f'{tenant_name} Overview - Critical Applications Dashboard',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/1d937bbe-0a45-47d1-88ca-ed2669ef7265'),
        (f'{tenant_name} Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/62c89b7b-f4eb-4e0b-89f6-7b0d65681216'),
        (f'{tenant_name} Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/91586cb3-91cb-48d1-98e6-8a4f0ff55683'),
        (f'{tenant_name} Problem Overview by Application',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/cf851de9-fa6f-415c-8d98-19426e8223bb'),
        (f'{tenant_name} Problem Overview by CMDBID',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/64ca2766-b0c6-4292-808c-7b65e16d4143'),
        (f'{tenant_name} Processes',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/0cf19c8e-2fb7-419a-9000-4cdd883d835c'),
        (f'{tenant_name} Service Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/8138cea4-9e0d-4420-a576-44e7dc6f4133'),
        (f'{tenant_name} Service Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/9c842a46-3f63-4919-877f-c5c281c14631'),
        (f'{tenant_name} Service HTTP Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/3cf16e7d-297f-4482-abcc-142da9fbbc10'),
        (f'{tenant_name} Service HTTP Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/83924c9d-47b7-4d98-971c-884005e27bd7'),
        (f'{tenant_name} Services By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/1c071505-bba5-441f-89c8-54eaac0e7f11'),
        (f'{tenant_name} Services',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/6e36671a-136e-4756-96b7-401026c52033'),
        (f'{tenant_name} Synthetics HTTP Monitors',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/1ad30fa0-3f3f-4588-9701-c04ef3440b28'),
        (f'{tenant_name} VMware',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/5f24c319-0230-4835-81f3-1e3b1d63c2a6'),
        (f'{tenant_name} Web Servers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/78aa8028-77b0-418c-86a7-4c70a7fa435b'),
        (f'{tenant_name} Web Servers',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/347eacdd-51f4-43bc-8e66-f96b19420905'),

        # (f'{tenant_name} Backend Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/b1cb4049-343a-4948-884a-055de4f102d1'),
        # (f'{tenant_name} Containers',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f72301b5-16f0-4937-80da-80220016bd8d'),
        # (f'{tenant_name} Full Stack Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/ac198ae8-bcd6-4e57-9edc-9cb13fe34bec'),
        # (f'{tenant_name} Go',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f6edd29f-785f-4443-a167-ff13db5be6d4'),
        # (f'{tenant_name} Hosts (Detailed)',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/c31f2e3c-cfa2-4ef8-acd2-71bd1a1347d1'),
        # (f'{tenant_name} Hosts',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/84a6068e-e74c-4d6c-a16a-6871bfbeb70d'),
        # (f'{tenant_name} Java Memory',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/28ce8409-a660-4b9e-9e7d-7f7ba3403b24'),
        # (f'{tenant_name} Network (Host-Level Details)',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/70a9d424-86ff-4879-bc67-587aefc55133'),
        # (f'{tenant_name} Network (Process-Level Details)',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/b2e07431-2fa3-4dca-8501-0ddf08d5d852'),
        # (f'{tenant_name} Node.js',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/4ca40110-d210-4dd7-91b7-3c902992d5ab'),
        # (f'{tenant_name} Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/91586cb3-91cb-48d1-98e6-8a4f0ff55683'),
        # (f'{tenant_name} Processes',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/0cf19c8e-2fb7-419a-9000-4cdd883d835c'),
        # (f'{tenant_name} Service Errors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/9c842a46-3f63-4919-877f-c5c281c14631'),
        # (f'{tenant_name} Service HTTP Errors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/83924c9d-47b7-4d98-971c-884005e27bd7'),
        # (f'{tenant_name} Services',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/6e36671a-136e-4756-96b7-401026c52033'),
        # (f'{tenant_name} Synthetics HTTP Monitors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/1ad30fa0-3f3f-4588-9701-c04ef3440b28'),
        # (f'{tenant_name} VMware' ,f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/5f24c319-0230-4835-81f3-1e3b1d63c2a6'),
        # (f'{tenant_name} Web Servers',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/347eacdd-51f4-43bc-8e66-f96b19420905'),

        # (f'{tenant_name}: Overview (Classic Dashboard)',
        #  f'https://{tenant}.live.dynatrace.com/#dashboard;id=00000000-dddd-bbbb-ffff-000000000001'),
        # (f'{tenant_name} Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/57b60014-c4ab-45f0-89e5-e4409a52734c'),
        # (f'{tenant_name} Citrix',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/f5426384-33e2-4704-bb69-7cd8ec60f46e'),
        # (f'{tenant_name} Hosts',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/598c7411-09bf-4ddb-9c1c-5ebbedef42a1'),
        # (f'{tenant_name} Hosts (Detailed)',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/2c7ec2c4-3091-4883-8346-35c62b24532a'),
        # (f'{tenant_name} Microsoft SQL Server Databases',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/7a0bbbce-83ea-43df-9ce8-b7fece2e13d0'),
        # (f'{tenant_name} Microsoft SQL Server External Extension Metrics: Combined',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/ded7d1ba-5b7d-4a09-8fb0-6c8a5995141f'),
        # (f'{tenant_name} Microsoft SQL Server External Extension Metrics: CPU/Memory',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/99c2879d-df7c-4b39-ad1e-92e76c5d9349'),
        # (f'{tenant_name} Microsoft SQL Server External Extension Metrics: Log',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/aa28a55a-9eaa-450e-9dbd-256695e371b6'),
        # (f'{tenant_name} Microsoft SQL Server External Extension Metrics: Transactions/Blocks/Locks/Latches',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/6e7f3443-7d55-4bf6-9377-0ae5997faa31'),
        # (f'{tenant_name} Microsoft SQL Server Online Databases',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/2a4efaaa-77ea-423d-a68f-942526668aa8'),
        # (f'{tenant_name} Microsoft SQL Server Recovering Databases',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/55d34ae6-c692-4dc6-9329-84abe94ebe04'),
        # (f'{tenant_name} Microsoft SQL Server Restoring Databases',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/5e64f169-18c1-411d-aff9-c981a6cb28e2'),
        # (f'{tenant_name} NetApp OnTap',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/38d4a3ff-b141-49b7-a159-40bb5f9f24a9'),
        # (f'{tenant_name} Netscaler 1',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/abe7d73b-66c7-4da2-bd90-bbb53ba86ad5'),
        # (f'{tenant_name} Netscaler 2',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/c2311d23-4be6-4219-8f67-5b9e26c5d21c'),
        # (f'{tenant_name} Network (Host-Level Details)',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/923d64cf-3734-4314-b4d4-a47f82025daa'),
        # (f'{tenant_name} Network (Process-Level Details)',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/d944955f-1879-4946-a705-a944dbd3ec1f'),
        # (f'{tenant_name} Oracle Database: ASM/Space',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/0afc5bb7-e707-46fd-a5fb-379a932bf5ce'),
        # (f'{tenant_name} Oracle Database: Combined',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/af83f2b3-08f4-4f87-ae25-1a20dfeda4e9'),
        # (f'{tenant_name} Oracle Database: CPU/Memory',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/c81dbfce-4803-4408-991a-81bdfc7f4c11'),
        # (f'{tenant_name} Oracle Database Host, Database, ASM Disk Lists',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/9caccc1d-5ec2-4ccb-95e0-e95c3c0294eb'),
        # (f'{tenant_name} Oracle Database: Redo Log/Reads/Writes',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/24b370e5-2826-4c9b-a7d2-13e62bce82f1'),
        # (f'{tenant_name} Oracle Database: Sessions/Users/Connections/Limits',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/3a25869e-3926-4df7-b3ec-fb232cc1ca78'),
        # (f'{tenant_name} Oracle Database: Times/Waits',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/2be33a10-76b5-4d0a-9357-6b801d443bb9'),
        # (f'{tenant_name} Processes',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/d1827cf5-2972-45ee-b1be-73d92bb2d9ba'),
        # (f'{tenant_name} Pure Storage FlashArray',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/3115bafc-90b4-48be-87b3-234dab3b22f2'),
        # (f'{tenant_name} Veritas',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/7662a958-d45d-439d-8f6a-92ba7f700a93'),
        # (f'{tenant_name} VMware Host',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/9b91cdd4-cbd0-4f44-8be8-ef2451cb966d'),
        # (f'{tenant_name} VMware Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/36775a56-6325-492c-9a2c-9025a458a774'),
        # (f'{tenant_name} VMware VM',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/5bb26f48-8e77-4aa1-af6f-4c29f18228a7'),

        # (f'{tenant_name} Backend Overview By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2e9b5aa4-9380-4dc4-a5d7-42c3febb9808'),
        # (f'{tenant_name} Backend Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=36730483-b704-444e-a5ff-15359903437a'),
        # (f'{tenant_name} Containers By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=11c84247-ce60-4292-8ee3-562a4887a7f4'),
        # (f'{tenant_name} Containers',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=93755756-640a-449c-950e-8a999267d85b'),
        # (f'{tenant_name} Full Stack Overview By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=489491b5-a999-435a-81bf-3a03f2353207'),
        # (f'{tenant_name} Full Stack Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0416be3a-4dc2-4852-9749-23ab9ff9c6f7'),
        # (f'{tenant_name} Go By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=22be2ba4-34df-4cef-afb0-bd74980adab0'),
        # (f'{tenant_name} Go',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=5c49a8c7-13e4-4137-b477-3e1386c9bd78'),
        # (f'{tenant_name} Java Memory By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8a5d30b1-1426-489f-bad0-59c59c70ffc7'),
        # (f'{tenant_name} Java Memory',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=66117e2a-545b-452a-93df-26817074dc84'),
        # (f'{tenant_name} NetApp OnTap Monitoring Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/com-dynatrace-extension-netapp-ontap-netapp-ontap-monitoring-overview--2074850867'),
        # (f'{tenant_name} Node.js By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4635787a-ef46-4213-9877-e836820da060'),
        # (f'{tenant_name} Node.js',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=89b87451-cf6f-4cf9-ac66-a44c825b303e'),
        # (f'{tenant_name} Service Errors By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d478262a-44b7-4882-8f2f-717c8deb9444'),
        # (f'{tenant_name} Service Errors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c6eeaeed-209c-480e-a827-7f4ce059186a'),
        # (f'{tenant_name} Service HTTP Errors By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a46a603c-b808-43db-b56c-e76bd8f0afe5'),
        # (f'{tenant_name} Service HTTP Errors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e230801e-7d2e-4845-ab16-eeaed8fe12d9'),
        # (f'{tenant_name} Services By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cebf26bb-0cee-456d-9af8-62225e5b42e9'),
        # (f'{tenant_name} Services',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a427698e-8125-4aec-9223-b01f6a08b70b'),
        # (f'{tenant_name} Synthetics HTTP Monitors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e0c86efb-8cc8-4ed9-a802-6fa507e55f01'),
        # (f'{tenant_name} VMware',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2ea1c750-5df7-423c-9bb0-0807154ad646'),
        # (f'{tenant_name} Web Servers By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=caac1d4e-ecb7-401c-bc52-8ff2343c634f'),
        # (f'{tenant_name} Web Servers',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=16c6d78e-1aa2-4466-a9c1-a9bdaced7356'),
    ]

    if tenant_name.lower() == 'prod':
        return prod_links
    else:
        print(f'Unsupported tenant name: {tenant_name}')
        exit(1)


def get_dashboard_links_by_management_zone(tenant_name, tenant):

    # Use add_environment_shares.py and generate_shared_document_links.py
    # to generate these lists

    prod_links = [
        (f'{tenant_name} Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/d3673a3e-27ca-48c2-b534-8fb2edb906a2'),
        (f'{tenant_name} Hosts By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/75d1d6c0-0531-477d-9d41-f67ef4ea1ddf'),
        (f'{tenant_name} Hosts (Detailed) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/72bbd5dd-e3bc-47a7-988d-83afa9000a1d'),
        (f'{tenant_name} Processes By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/39d0812f-1450-49e3-80c5-744392aea715'),
        (f'{tenant_name} Network (Host-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/9d29fe3c-58f9-4f7b-97dc-341ebce78ea2'),
        (f'{tenant_name} Network (Process-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/eacc600b-46e5-4b7d-ae0c-0b3219f75024'),
        # (f'{tenant_name} Backend Overview By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2e9b5aa4-9380-4dc4-a5d7-42c3febb9808'),
        # (f'{tenant_name} Backend Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=36730483-b704-444e-a5ff-15359903437a'),
        # (f'{tenant_name} Containers By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=11c84247-ce60-4292-8ee3-562a4887a7f4'),
        # (f'{tenant_name} Containers',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=93755756-640a-449c-950e-8a999267d85b'),
        # (f'{tenant_name} Full Stack Overview By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=489491b5-a999-435a-81bf-3a03f2353207'),
        # (f'{tenant_name} Full Stack Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0416be3a-4dc2-4852-9749-23ab9ff9c6f7'),
        # (f'{tenant_name} Go By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=22be2ba4-34df-4cef-afb0-bd74980adab0'),
        # (f'{tenant_name} Go',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=5c49a8c7-13e4-4137-b477-3e1386c9bd78'),
        # (f'{tenant_name} Java Memory By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8a5d30b1-1426-489f-bad0-59c59c70ffc7'),
        # (f'{tenant_name} Java Memory',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=66117e2a-545b-452a-93df-26817074dc84'),
        # (f'{tenant_name} NetApp OnTap Monitoring Overview',
        #  f'https://{tenant}.apps.dynatrace.com/ui/apps/dynatrace.dashboards/dashboard/com-dynatrace-extension-netapp-ontap-netapp-ontap-monitoring-overview--2074850867'),
        # (f'{tenant_name} Node.js By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4635787a-ef46-4213-9877-e836820da060'),
        # (f'{tenant_name} Node.js',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=89b87451-cf6f-4cf9-ac66-a44c825b303e'),
        # (f'{tenant_name} Service Errors By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d478262a-44b7-4882-8f2f-717c8deb9444'),
        # (f'{tenant_name} Service Errors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c6eeaeed-209c-480e-a827-7f4ce059186a'),
        # (f'{tenant_name} Service HTTP Errors By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a46a603c-b808-43db-b56c-e76bd8f0afe5'),
        # (f'{tenant_name} Service HTTP Errors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e230801e-7d2e-4845-ab16-eeaed8fe12d9'),
        # (f'{tenant_name} Services By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cebf26bb-0cee-456d-9af8-62225e5b42e9'),
        # (f'{tenant_name} Services',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a427698e-8125-4aec-9223-b01f6a08b70b'),
        # (f'{tenant_name} Synthetics HTTP Monitors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e0c86efb-8cc8-4ed9-a802-6fa507e55f01'),
        # (f'{tenant_name} VMware',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2ea1c750-5df7-423c-9bb0-0807154ad646'),
        # (f'{tenant_name} Web Servers By Management Zone',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=caac1d4e-ecb7-401c-bc52-8ff2343c634f'),
        # (f'{tenant_name} Web Servers',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=16c6d78e-1aa2-4466-a9c1-a9bdaced7356'),
    ]

    if tenant_name.lower() == 'prod':
        return prod_links
    else:
        print(f'Unsupported tenant name: {tenant_name}')
        exit(1)


def get_links():
    links = [
        ('What is Dynatrace', 'https://docs.dynatrace.com/docs/shortlink/intro'),
        ('Navigate the Dynatrace platform', 'https://docs.dynatrace.com/docs/shortlink/navigation'),
        ('Platform search', 'https://docs.dynatrace.com/docs/shortlink/platform-search'),
        ('Dashboards', 'https://docs.dynatrace.com/docs/shortlink/dashboards'),
        ('Notebooks', 'https://docs.dynatrace.com/docs/shortlink/notebooks'),
        ('Launchpads', 'https://docs.dynatrace.com/docs/shortlink/launchpads'),
        ('Dynatrace Apps', 'https://docs.dynatrace.com/docs/shortlink/dynatrace-apps'),
        # ('Dynatrace Developer', 'https://developer.dynatrace.com/'),
        ('Introduction to workflows', 'https://docs.dynatrace.com/docs/shortlink/workflows'),
        ('Dynatrace Query Language', 'https://docs.dynatrace.com/docs/shortlink/dql-dynatrace-query-language-hub'),
        ('Dynatrace Pattern Language', 'https://docs.dynatrace.com/docs/shortlink/dpl-dynatrace-pattern-language-hub'),
        ('Dashboards Classic', 'https://docs.dynatrace.com/docs/shortlink/dashboards-hub'),
        # ('Services App', 'https://docs.dynatrace.com/docs/shortlink/services-app'),
        # ('Services', 'https://docs.dynatrace.com/docs/shortlink/services'),
        # ('Service analysis (classic page)', 'https://docs.dynatrace.com/docs/shortlink/services-analysis'),
        # ('Databases', 'https://docs.dynatrace.com/docs/shortlink/databases-hub'),
        # ('Message queues', 'https://docs.dynatrace.com/docs/shortlink/queues-hub'),
        # ('Distributed Tracing', 'https://docs.dynatrace.com/docs/shortlink/distributed-traces-grail'),
        ('Log Content Analysis', 'https://docs.dynatrace.com/docs/shortlink/lma-analysis'),
        ('Metrics', 'https://docs.dynatrace.com/docs/shortlink/metrics-grail'),
        # ('Profiling and optimization', 'https://docs.dynatrace.com/docs/shortlink/profiling-optimization'),
        # ('Real User Monitoring concepts', 'https://docs.dynatrace.com/docs/shortlink/basic-concepts-landing'),
        # ('Web applications', 'https://docs.dynatrace.com/docs/shortlink/web-applications-landing'),
        # ('Session segmentation', 'https://docs.dynatrace.com/docs/shortlink/user-sessions-landing'),
        # ('Session Replay', 'https://docs.dynatrace.com/docs/shortlink/session-replay'),
        # ('Synthetic Monitoring', 'https://docs.dynatrace.com/docs/shortlink/synthetic-hub'),
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
        ('Dynatrace Essentials Learning Plan', 'https://university.dynatrace.com/learn/learning-plans/31/dynatrace-essentials-learning-plan'),
    ]

    return links


def generate_markdown_block(block_name, links):
    launchpad_block = copy.deepcopy(launchpad_markdown_block_template)
    shared_markdown_string = f'#  {block_name}  \n'

    for link in links:
        link_markdown = f'[{link[0]}]({link[1]})  \n'
        shared_markdown_string += link_markdown

    global id_index
    launchpad_block['id'] = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeee' + str(id_index)
    id_index += 1
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

    # print(launchpad_block)

    return launchpad_block


def get_ready_made_dashboard_links(env, client_id, client_secret):
    ignore_ready_made_dashboards = [
        'Citrix DaaS & Virtual Apps and Desktops Overview',
        'Classic Azure overview',
        'Digital Experience retain and query usage',
        'Frontend resource analysis',
        'Page performance & errors',
        'User sessions overview',
        'XHR performance',
    ]
    selected_ready_made_dashboards = [
        # 'AWS API',
        # 'AWS Bedrock',
        # 'AWS DynamoDB',
        # 'AWS EC2',
        # 'AWS ECS',
        # 'AWS EFS',
        # 'AWS EKS',
        # 'AWS ELB',
        # 'AWS Edge Networking',
        # 'AWS ElastiCache',
        # 'AWS EventBridge',
        # 'AWS Foundation Networking',
        # 'AWS Health Events',
        # 'AWS Lambda',
        # 'AWS Managed Streaming for Apache Kafka',
        # 'AWS Overview',
        # 'AWS RDS',
        # 'AWS S3',
        # 'AWS SNS',
        # 'AWS SQS',
        'ActiveGate diagnostic overview',
        'Cisco Device Overview',
        'Cisco UCS C-Series Overview',
        'Cisco UCS M-Series Overview',
        'Citrix DaaS & Virtual Apps and Desktops Overview',
        # 'Classic AWS overview',
        'Classic Azure overview',
        'Custom Alerts Health Dashboard',
        'Databases Overview',
        'Digital Experience retain and query usage',
        'Endpoint Cardinality Dashboard',
        'Extension data consumption',
        'Frontend resource analysis',
        'Full-Stack Adaptive Traffic Management and trace capture',
        'Generative AI feature adoption',
        'Generic network overview',
        'Getting started with Dashboards',
        'HP iLO Overview',
        'IBM i Overview',
        'Infoblox Overview',
        'Infrastructure Observability Dashboard',
        # 'Kubernetes cluster',
        # 'Kubernetes monitoring statistics',
        # 'Kubernetes namespace - pods',
        # 'Kubernetes namespace - workloads',
        # 'Kubernetes node - pods',
        # 'Kubernetes persistent volumes',
        'Log ingest overview',
        'Log query usage and costs',
        'Messaging Destination Dashboard',
        'Microsoft Active Directory monitoring Overview',
        # 'Mobile app start health',
        # 'Mobile troubleshooting',
        'NetApp OnTap Monitoring Overview',
        'NetScaler ADC Overview',
        'NetScaler SDX Overview',
        'Network analytics',
        'Network devices',
        'Network performance',
        'Nutanix Overview',
        'OpenPipeline usage overview',
        'Oracle Autonomous Database on OCI Overview',
        'Oracle Cloud Infrastructure Overview',
        'Oracle DB Overview',
        'Oracle Database Clusters on OCI Overview',
        'Page performance & errors',
        'Pure Storage FlashArray Overview',
        'SQL Server (Local) Overview',
        'SQL Server Locks',
        'SQL Server Overview',
        'SQL Server Performance Counters Overview',
        # 'Security Posture overview',
        'Synthetic network availability monitoring',
        'Synthetic web availability and performance',
        'User sessions overview',
        'VMware Extension Overview',
        'Veritas Netbackup Overview',
        # 'Vulnerability Coverage',
        'XHR performance',
    ]
    dynatrace_owner1 = '50436aec-8901-4282-ae81-690bd6509b18'
    dynatrace_owner2 = '60a34747-becc-47c2-ac3a-bfaf2c537471'
    dynatrace_owner3 = 'ed29e85d-9e5f-4157-a2b8-563dc624708f'

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

            # print(document_name, document_owner)

            if document_owner == dynatrace_owner1 or document_owner == dynatrace_owner2 or document_owner == dynatrace_owner3:
                # if document_name in selected_ready_made_dashboards:
                if document_name == 'Classi AWS Overview':
                    rows.append([document_name, document_id])
                else:
                    if document_name not in ignore_ready_made_dashboards and 'Mobile' not in document_name and 'AWS' not in document_name and 'Azure' not in document_name:
                        # print('ADDING', document_name, document_owner)
                        rows.append([document_name, document_id])

    return sorted(rows)


def generate_application_block():
    filename = 'Assets/Quick Application List.json'
    with codecs.open(filename, encoding='utf-8') as f:
        document = f.read()
        document_json = json.loads(document)
        block = document_json.get('containerList').get('containers')[0].get('blocks')[0]
        launchpad_block = copy.deepcopy(block)
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
