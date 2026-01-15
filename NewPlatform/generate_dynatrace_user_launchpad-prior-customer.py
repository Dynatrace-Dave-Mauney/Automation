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

    # Use generate_shared_document_links.py to generate these lists

    sandbox_links = [
        (f'{tenant_name} Backend Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e05ec075-8ce3-4fab-8de9-ba63f5941fa7'),
        (f'{tenant_name} Backend Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b1363663-878b-4020-8553-cacfb9fd2fc1'),
        (f'{tenant_name} Containers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=671859eb-5950-4f32-ac5b-6d63f77dbc46'),
        (f'{tenant_name} Containers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=21aae6f2-1874-450c-bc70-c7c2b833e0f2'),
        (f'{tenant_name} Full Stack Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=79850057-0611-4510-8857-592cfabcd196'),
        (f'{tenant_name} Full Stack Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=32f170a0-ad70-42f8-8f44-9ebb04a48834'),
        (f'{tenant_name} Go By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e2ff2c9e-c532-4ce5-b1e7-6fbcd78a5fda'),
        (f'{tenant_name} Go',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=243dd0ad-9e1b-4160-a8e7-a8f797358bc1'),
        (f'{tenant_name} Hosts (Detailed) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0cd2c2dc-74b6-4832-8e33-0ca769fbd982'),
        (f'{tenant_name} Hosts (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=43f0d183-caa4-4dc6-af99-d25c23e425c8'),
        (f'{tenant_name} Hosts By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9c7a55d7-07af-493c-ae47-b29852627a6f'),
        (f'{tenant_name} Hosts',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=08c7caeb-593f-44f7-b490-f37d9f449880'),
        (f'{tenant_name} Java Memory By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=035db63c-60da-4a86-a544-91e1aeeba8f7'),
        (f'{tenant_name} Java Memory',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b8f57c45-e8dc-41f0-bc33-2651fd93fe6e'),
        (f'{tenant_name} Network (Host-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=1e17d7d5-d571-41da-9ef5-01a9c59233e7'),
        (f'{tenant_name} Network (Host-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c0bc012b-8b6e-4033-b34a-a751d51bfab4'),
        (f'{tenant_name} Network (Process-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a0acf3b3-7de1-41de-a8c3-f09a99e74846'),
        (f'{tenant_name} Network (Process-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9d6bfb91-17d3-442d-ae48-f3be9666a34e'),
        (f'{tenant_name} Node.js By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f43d8eb2-c590-483e-9140-0706e4da2ebe'),
        (f'{tenant_name} Node.js',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=13c7b2d8-2592-4752-97fe-e1722f1d0275'),
        (f'{tenant_name} Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=603964de-ba81-4cf7-a7c4-7b21b9ea9462'),
        (f'{tenant_name} Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8a037f13-4227-43b8-8308-c12cf961574d'),
        (f'{tenant_name} Service Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=ab24cbbc-018a-4739-8f01-fa708b4b150d'),
        (f'{tenant_name} Service Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0841bc3e-ecfb-4822-951b-c3ffa346cb88'),
        (f'{tenant_name} Service HTTP Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e31cc73b-6c4e-4f42-a991-d5199587fe93'),
        (f'{tenant_name} Service HTTP Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0705dda6-98cf-4f25-a0a3-0e10942ac371'),
        (f'{tenant_name} Services By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=75001142-f6f7-49da-92cb-2c2f51faed39'),
        (f'{tenant_name} Services',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=269ca379-9b2c-4923-a51a-81d6a5704b27'),
        (f'{tenant_name} Synthetics HTTP Monitors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=5464b22f-0c6d-4517-8e04-4021a2016642'),
        (f'{tenant_name} VMware',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=356f68b9-cf99-41c4-b140-0de5af99ae0b'),
        (f'{tenant_name} Web Servers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c8bae8e0-ce34-4370-a36d-e44c25d676cd'),
        (f'{tenant_name} Web Servers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f243bcc4-3243-4d56-b518-271803650d85'),
    ]

    preprod_links = [
        (f'{tenant_name} Backend Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f96cb6f1-7f6b-4730-90b7-10401fefe32d'),
        (f'{tenant_name} Backend Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=68840b3a-68e0-43d7-8db9-d83c908d844c'),
        (f'{tenant_name} Containers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c577c327-fb8b-44d9-abc4-c7e71c8e679e'),
        (f'{tenant_name} Containers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=af4cdbf3-aa97-4adf-b461-506990bb272c'),
        (f'{tenant_name} Full Stack Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2e79ce2f-2c5c-4eba-9b52-192bd775be49'),
        (f'{tenant_name} Full Stack Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d65b659f-a8fc-441e-9885-ec8fc45cbfde'),
        (f'{tenant_name} Go By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a00db3bf-bcc8-4159-974c-6f6f78a75731'),
        (f'{tenant_name} Go',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e629b48e-9514-4f88-996c-990473019cb2'),
        (f'{tenant_name} Hosts (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6c1fba79-dd9f-4c06-a899-cd984055a004'),
        (f'{tenant_name} Hosts By Management Zone (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8c64dadc-eec5-45b9-9e74-798967b1fd59'),
        (f'{tenant_name} Hosts By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2223b144-2c61-46c9-98b3-c2786c7529f8'),
        (f'{tenant_name} Hosts',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e32b503a-e69c-48df-9220-bbce7364e9f7'),
        (f'{tenant_name} Java Memory By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c062df64-2bf9-4117-bbdc-79ccacc78b09'),
        (f'{tenant_name} Java Memory',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d3022e5e-d291-438d-9aaa-c40d17e59c03'),
        (f'{tenant_name} Network (Host-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2afcb124-352e-43f4-b580-7833102590e8'),
        (f'{tenant_name} Network (Host-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=06647289-c1bc-4642-8660-b94059247879'),
        (f'{tenant_name} Network (Process-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4bb330cb-2813-4307-b28e-cc1c8a9aa633'),
        (f'{tenant_name} Network (Process-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=65a81ec0-f690-46c6-972a-641fdb525ec9'),
        (f'{tenant_name} Node.js By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=083f851d-f27b-48c4-8c13-fcd6b6a8f354'),
        (f'{tenant_name} Node.js',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=47d06727-bb6b-4b4c-bbe8-f2879cbe8c9a'),
        (f'{tenant_name} Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f01fc1de-9af2-49bc-835c-a32b68fdd7d1'),
        (f'{tenant_name} Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c4d96ab9-6cb7-4869-a3fd-be8bc7d83fbe'),
        (f'{tenant_name} Service Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a6133269-6396-4fd9-a5a4-69c4dbaca1fb'),
        (f'{tenant_name} Service HTTP Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cf116508-a158-4e06-8311-e4ff59ab5ca5'),
        (f'{tenant_name} Service HTTP Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9142c724-aa5e-43a7-aff3-246c3ba80af8'),
        (f'{tenant_name} Services By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6aa9a5a8-ee8a-4471-80d5-77a781b30b98'),
        (f'{tenant_name} Services',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=59e6c8f9-ccc5-44d8-8ef7-49f2d1542202'),
        # (f'{tenant_name} Synthetics HTTP Monitors',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=fd223411-9a7a-4fdc-b19a-1e922096962c'),
        # (f'{tenant_name} Usage Details',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c8e157bf-e097-4d1c-b8ca-a55f4ca639f2'),
        # (f'{tenant_name} Usage',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=527d9109-0346-4d3c-aaaf-3bf10e70eab9'),
        # (f'{tenant_name} VMware',
        #  f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=58eea538-d762-4c66-ba26-651055e52c66'),
        (f'{tenant_name} Web Servers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=5b62a252-2ef4-49e3-b5f7-c152441b7afc'),
        (f'{tenant_name} Web Servers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d46133c0-f2b7-4694-8b5b-cb065516fd95'),
    ]

    prod_links = [
        (f'{tenant_name} Backend Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=521bbcb0-54ea-4075-9a1e-eebd73f835a2'),
        (f'{tenant_name} Backend Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=bbf81c7f-c89b-4dd4-9bab-2caac254422a'),
        (f'{tenant_name} Containers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4c573952-43c2-4006-b22d-f4125fdfbbfa'),
        (f'{tenant_name} Containers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=3db6c662-912c-427c-859c-9e7e8f0a1a9e'),
        (f'{tenant_name} Full Stack Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b3a7a1f4-1b44-4b35-ae52-2ce29b7876c7'),
        (f'{tenant_name} Full Stack Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=1028f289-b45f-44f8-9142-5f0f2e4e99b7'),
        (f'{tenant_name} Go By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=26fccdd4-6b5c-4b74-a851-a54bd5566597'),
        (f'{tenant_name} Go',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=66c807c0-8923-46c8-ba1a-fdded2cb2e94'),
        (f'{tenant_name} Hosts (Detailed) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f7afebec-0890-4222-a195-fb68d1147812'),
        (f'{tenant_name} Hosts (Detailed)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=44c34c67-b722-46b0-b25b-c96614f8cc0d'),
        (f'{tenant_name} Hosts By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=941e6c59-8263-475e-ba5c-6238ec7a644f'),
        (f'{tenant_name} Hosts',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8ff45bc3-c4b1-4bf6-8306-62d8bf5072a4'),
        (f'{tenant_name} Java Memory By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=25faf792-55ba-4821-b4b2-140b33013a5c'),
        (f'{tenant_name} Java Memory',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b019af2b-ac82-44ae-bf18-49c7f87080c4'),
        (f'{tenant_name} Network (Host-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=e2a61415-2aaa-45e6-aa27-cbe90096be55'),
        (f'{tenant_name} Network (Host-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a3c22337-2153-4c4a-9148-aa91f039905c'),
        (f'{tenant_name} Network (Process-Level Details) By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9d6a64cc-ac20-4166-b7c7-69e9f125d745'),
        (f'{tenant_name} Network (Process-Level Details)',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4c88ec9f-de9d-4f0a-9bbb-2c92de1de7bb'),
        (f'{tenant_name} Node.js By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=17bf5647-df13-4320-9657-849f3ba78023'),
        (f'{tenant_name} Node.js',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=20fa4b8b-4563-430c-8687-ceeb7355c04f'),
        (f'{tenant_name} Overview By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=030385f9-abad-410a-9834-3ca0bfd91877'),
        (f'{tenant_name} Overview',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=724ddc29-e87f-48ae-b978-385351c65185'),
        (f'{tenant_name} Service Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b19df785-08b3-44af-b7ad-a765d8696426'),
        (f'{tenant_name} Service Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b30c6bf7-b23f-4822-b0cc-a7f5d8b189a0'),
        (f'{tenant_name} Service HTTP Errors By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=26ca2fab-f220-4029-bd4d-1b95423d7e83'),
        (f'{tenant_name} Service HTTP Errors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=1535dfd9-36ac-4902-83d2-c18297006bd3'),
        (f'{tenant_name} Services By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=54970e44-8ee0-46fd-9b4f-96bf3efd3d9d'),
        (f'{tenant_name} Services',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=831b8a27-45a5-486e-a376-1c094fe1eb85'),
        (f'{tenant_name} Synthetics HTTP Monitors',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=81c921ef-9d72-4b72-ad1e-9c909890c533'),
        (f'{tenant_name} VMware',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c4c85016-b2fa-45d8-bc48-735fcfba6dff'),
        (f'{tenant_name} Web Servers By Management Zone',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=43e20166-32ef-4a8f-9216-153375ac99cf'),
        (f'{tenant_name} Web Servers',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=91ea9dfc-5fc6-407e-8d96-bf12400396de'),
        (f'{tenant_name}',
         f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c89e6fe4-ec2c-46d8-b17d-c16878e29a17'),
    ]

    # Prior Customer
    # sandbox_links = [
    #     (f'{tenant_name} Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=cf48719e-9e5f-42b1-902e-d118cabbe6df'),
    #     (f'{tenant_name} Services',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6ef4c6cb-7fc0-4871-bebe-4c527fe8da03'),
    #     (f'{tenant_name} Service Errors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9cf2cdec-e883-4497-a365-b4fd047a7cd8'),
    #     (f'{tenant_name} Service HTTP Errors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f0ad8bd8-4cdd-4ec6-a483-13eed9074761'),
    #     (f'{tenant_name} Synthetics HTTP Monitors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=14784246-597a-475a-b950-35c3602ded84'),
    #     (f'{tenant_name} Hosts (Detailed)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=8b56dbd9-598c-412b-927e-426ec8465cb2'),
    #     (f'{tenant_name} Hosts',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a6295b0a-0d82-42b2-a430-c0e7b69cf85c'),
    #     (f'{tenant_name} Network (Host-Level Details)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d8f2e522-f16b-4666-bdef-6a63a18b54b4'),
    #     (f'{tenant_name} Network (Process-Level Details)',
    #      'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c5ac91a0-3037-41db-bdd5-2e4deaf6a382'),
    #     (f'{tenant_name} VMware',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=62dd2a66-3bf9-4e62-a7e3-759006a79453'),
    #     (f'{tenant_name} Containers',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d87c28fa-b052-425a-acbd-e42684b63bdb'),
    #     (f'{tenant_name} Full Stack Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=43509742-c2e9-44a5-a501-fb9c75b45264'),
    #     (f'{tenant_name} Backend Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b9b6498c-222a-4eaf-9025-e344c9e3f183'),
    #     (f'{tenant_name} Java Memory',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=f373d6f4-2138-41b3-b9c1-8355c52b0b1b'),
    #     (f'{tenant_name} Go',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=26568803-df30-4999-bc50-748ce1df22ce'),
    #     (f'{tenant_name} Node.js',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=4a98b69e-826c-400b-a17a-80aaabdb9089'),
    #     (f'{tenant_name} Web Servers',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0845de3e-ef7e-46f0-b65a-32e4504b1f24'),
    # ]
    #
    # prod_links = [
    #     (f'{tenant_name} Backend Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=00206100-59f6-4e6f-9fd6-90d0d238b2ba'),
    #     (f'{tenant_name} Containers',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=13f0f6c0-2d67-4ca0-8b3b-50b430e82c84'),
    #     (f'{tenant_name} Full Stack Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0959f255-1cac-425b-a4a5-fe0d5e8e0c81'),
    #     (f'{tenant_name} Go',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9642e785-f478-4edd-8382-32385db1e4d1'),
    #     (f'{tenant_name} Hosts (Detailed)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a7a3ba73-e488-499f-bb10-640aab1f4070'),
    #     (f'{tenant_name} Hosts',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=37b19613-355e-4fe7-bdcb-09079963187e'),
    #     (f'{tenant_name} Java Memory',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6ec9377e-8724-4b92-bfef-926a433612f6'),
    #     (f'{tenant_name} Network (Host-Level Details)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=63c1cd51-54a6-4ea5-9ae9-cc174241aae9'),
    #     (f'{tenant_name} Network (Process-Level Details)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=58ffdc1f-f924-4817-9293-326f02d7552b'),
    #     (f'{tenant_name} Node.js',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=683a9aed-b5c1-42b4-8afa-b0378e4453ca'),
    #     (f'{tenant_name} Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6ea10cc4-6357-4395-9639-af657aaf9005'),
    #     (f'{tenant_name} Service Errors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9db8895d-29d0-477d-9276-577594abb835'),
    #     (f'{tenant_name} Service HTTP Errors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=0b62c3ba-544c-4a4f-bf76-8c011181f94b'),
    #     (f'{tenant_name} Services',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=df3a8e8f-ef4f-4786-8527-cc8c73e3728a'),
    #     (f'{tenant_name} Synthetics HTTP Monitors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9306db61-9262-4142-b82a-9e07143e2df7'),
    #     (f'{tenant_name} VMware',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2d23eb94-d65a-4c15-be24-5afb715371ad'),
    #     (f'{tenant_name} Web Servers',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=a0813f89-f1af-40c3-afdc-78ee7598b0f5'),
    # ]
    #
    # nonprod_links = [
    #     (f'{tenant_name} Backend Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=5eae3a22-ba64-4cdd-9e78-501f6ae2db63'),
    #     (f'{tenant_name} Containers',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=40a56662-cffa-4e17-a14e-ae226de1502e'),
    #     (f'{tenant_name} Full Stack Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c3e42dfe-461d-4cd4-bd01-e8c0c1300c48'),
    #     (f'{tenant_name} Go',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=78ce89dd-20dd-4884-a065-123af95a188e'),
    #     (f'{tenant_name} Hosts (Detailed)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=1a45e197-bfad-4080-bef4-d8d3b1a47ba0'),
    #     (f'{tenant_name} Hosts',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=c44f8fb9-1610-41c7-8eba-490ebcf38222'),
    #     (f'{tenant_name} Java Memory',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=9ed5fb56-50c4-4b1c-a397-cc6fa3f79774'),
    #     (f'{tenant_name} Network (Host-Level Details)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2a5023be-7c4f-4490-8a8b-63767ccdf910'),
    #     (f'{tenant_name} Network (Process-Level Details)',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=6bcce121-4948-44a1-b11b-3fbfe9c30b00'),
    #     (f'{tenant_name} Node.js',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=2702b036-93c9-439f-b1f7-6889088b5b6e'),
    #     (f'{tenant_name} Overview',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=19026ded-eba1-4f9c-9b4a-43f44ba67aa8'),
    #     (f'{tenant_name} Service Errors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=b1dfc7c0-ea2d-4056-a519-f29259e04c07'),
    #     (f'{tenant_name} Service HTTP Errors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=eec1899e-7709-4d8f-b82c-f6d87d3be90e'),
    #     (f'{tenant_name} Services',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=034f8f8b-bac7-4424-b936-40e75573f461'),
    #     (f'{tenant_name} Synthetics HTTP Monitors',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=58597239-cec7-4a0a-a3d8-65c95c3fcfcd'),
    #     (f'{tenant_name} VMware',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=d5c70dfe-51c4-444a-8586-e9bdc720c76e'),
    #     (f'{tenant_name} Web Servers',
    #      f'https://{tenant}.apps.dynatrace.com/ui/document/v0/#share=102a0efa-df17-4564-b52e-07a7271a5cb3'),
    # ]

    if tenant_name.lower() == 'sandbox':
        return sandbox_links
    else:
        if tenant_name.lower() == 'preprod':
            return preprod_links
        else:
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
        'ActiveGate diagnostic overview',
        'Azure overview',
        # 'Cisco Device Overview',
        # 'Databases Overview',
        'Extension Data Consumption',
        'Full-Stack Adaptive Traffic Management and trace capture',
        'Getting started',
        # 'IBM MQ Monitoring Overview',
        'Infrastructure Observability Dashboard',
        # 'Kafka Overview',
        'Kubernetes Cluster',
        'Kubernetes Namespace - Pods',
        'Kubernetes Namespace - Workloads',
        'Kubernetes Node - Pods',
        'Kubernetes Persistent Volumes',
        'Log ingest overview',
        'Log query usage and costs',
        # 'Network analytics',
        # 'Network availability monitoring',
        # 'Network devices',
        # 'Network performance',
        # 'Nutanix Overview',
        'OpenPipeline usage overview',
        # 'Oracle DB Overview',
        # 'SQL Server Overview',
        # 'VMware Extension Overview',
        # 'Web availability and performance',
    ]

    # A Prior Customer
    # selected_ready_made_dashboards = [
    #     'AWS overview',
    #     'ActiveGate diagnostic overview',
    #     'Azure overview',
    #     'Cisco Device Overview',
    #     'Databases Overview',
    #     'Extension Data Consumption',
    #     'F5 BIG-IP DNS Overview',
    #     'F5 BIG-IP LTM Overview',
    #     'F5 BIG-IP LTM Status',
    #     'Getting started',
    #     'IBM Datapower Overview',
    #     'IBM MQ Monitoring Overview',
    #     'Infrastructure Observability Dashboard',
    #     'Kafka Overview',
    #     'Kubernetes Cluster',
    #     'Kubernetes Namespace - Pods',
    #     'Kubernetes Namespace - Workloads',
    #     'Kubernetes Node - Pods',
    #     'Kubernetes Persistent Volumes',
    #     'Log ingest overview',
    #     'Log query usage and costs',
    #     'Network analytics',
    #     'Network availability monitoring',
    #     'Network devices',
    #     'Network performance',
    #     'Nutanix Overview',
    #     'Oracle DB Overview',
    #     'SQL Server Overview',
    #     'Salesforce Data Ingest Overview',
    #     'Salesforce Ingest and Outage',
    #     'Salesforce Overview',
    #     'Salesforce Pages with Timeouts',
    #     'Salesforce User Activity Deep Dive',
    #     'VMware Extension Overview',
    #     'Web availability and performance',
    # ]
    # dynatrace_owner = 'ed29e85d-9e5f-4157-a2b8-563dc624708f'
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
        # 'AWS Classic',
        # 'AWS overview',
        'Azure overview',
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
        'Logs & Events Classic',
        'Multidimensional Analysis',
        'Notebooks',
        'Problems',
        'Problems Classic',
        'Segments',
        'Service-Level Objectives',
        'Service-Level Objectives Classic',
        'Services',
        'Services Classic',
        'Technologies & Processes Classic',
        # 'VMware Classic',
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
    # env_name_supplied = 'PreProd'
    # env_name_supplied = 'Sandbox'
    # env_name_supplied = 'Personal'
    env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
    process(env_name, env, client_id, client_secret)


if __name__ == '__main__':
    main()
