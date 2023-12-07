from inspect import currentframe
import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

# target_hosts = [
#     'HOST-0066227A7020E61D',
#     'HOST-0153586CE7A124AD',
#     'HOST-01BB32003FDDAE63',
#     'HOST-01FF4D2ABFACB2C9',
#     'HOST-02C31139E5D95275',
#     'HOST-036C869E7DC4D6D4',
#     'HOST-045B17AEA391F0AB',
#     'HOST-04B0FC75567AC00B',
#     'HOST-05EEF12651A0D2CA',
#     'HOST-0656C2819F2C20E7',
#     'HOST-06AD47B9269716F3',
#     'HOST-0B186D4FDD77F5EB',
#     'HOST-0D112247D282DB03',
#     'HOST-0EDBC26004AB4C72',
#     'HOST-0F78F2A7D73C2155',
#     'HOST-10A7CD51C5BA3523',
#     'HOST-14A52250E3DB84BF',
#     'HOST-18B7E723F4440D23',
#     'HOST-1927894663B561FC',
#     'HOST-1AC655671ED188BD',
#     'HOST-1CC9F34AEF917C55',
#     'HOST-1DDF671B5AD6F6F1',
#     'HOST-1E487D8A90731EEE',
#     'HOST-21973A0E1E39BD92',
#     'HOST-21E5526845DAF4BB',
#     'HOST-23BBC179F04E3BF3',
#     'HOST-2466EF9DCBCDAF16',
#     'HOST-254671A9A675BB27',
#     'HOST-25D8A6D8727DBAC8',
#     'HOST-29BEA52B855AC209',
#     'HOST-2B0832397E87449C',
#     'HOST-2FE71F4B8CDDACAE',
#     'HOST-33DC981DEE091A52',
#     'HOST-34DE6BE8EDEE9925',
#     'HOST-351126D0F4CFAAE6',
#     'HOST-36FA308FE395FEED',
#     'HOST-39657D66A2C81603',
#     'HOST-39E46E413F5D586E',
#     'HOST-39E7ED172032273F',
#     'HOST-3A9B0A2B201533E5',
#     'HOST-3C5C7AE55EF24CC4',
#     'HOST-4062D332ABEA06DE',
#     'HOST-4569A26D602F6206',
#     'HOST-4591497654653B5B',
#     'HOST-464D592354D37418',
#     'HOST-48535EE25FAFAAE5',
#     'HOST-48E0E5F4AC3193B7',
#     'HOST-4981190E958FD76B',
#     'HOST-4AB1C33DF74326EC',
#     'HOST-4BB0B970AD465EC4',
#     'HOST-4BCB0C5F7188B46A',
#     'HOST-5CD012EDA56752F4',
#     'HOST-5D21121947A75110',
#     'HOST-5F139AE5162A2B5C',
#     'HOST-6147083624283FCA',
#     'HOST-634438B6B477FAC1',
#     'HOST-6453DA44F72BBEF5',
#     'HOST-64A295DE3F6D4944',
#     'HOST-65E47D786F451258',
#     'HOST-6B8E77827F78368B',
#     'HOST-6E359D518496719D',
#     'HOST-70D228C8BBAD428F',
#     'HOST-76C09EE606A3F008',
#     'HOST-7AC6A3C114A5A578',
#     'HOST-7D2928C430010C3B',
#     'HOST-7EE0C8D34F5EDE79',
#     'HOST-80AEF9A725E58B62',
#     'HOST-8108AB5EF93A91D8',
#     'HOST-81F44346E9934935',
#     'HOST-82128D03CCF9489A',
#     'HOST-83BD6A03FF140D36',
#     'HOST-84B5F89A53887A01',
#     'HOST-8697CD2D68E51836',
#     'HOST-8744FA8AC45BD857',
#     'HOST-88FB111E64080E4A',
#     'HOST-8C8741DBCDCC37B3',
#     'HOST-8CB25EE4CE1E096A',
#     'HOST-8D92DADCEDCBB909',
#     'HOST-93573CD4277B4F0E',
#     'HOST-96FCCD5EE6066C8A',
#     'HOST-986EC7D08872235A',
#     'HOST-98FC747893143080',
#     'HOST-9A6142C500696250',
#     'HOST-9AEE14D79CEA64C9',
#     'HOST-9B128EBA5B458D24',
#     'HOST-9B508874FAD836B2',
#     'HOST-9E99564A0EC3ACAF',
#     'HOST-9FB79074D5460BDF',
#     'HOST-A2D3DB82932714D8',
#     'HOST-A303F1C3B4D95CF2',
#     'HOST-A6674A6C89199B89',
#     'HOST-A93DAC3033377C92',
#     'HOST-ADEF11BE602F4604',
#     'HOST-ADF6C3F8CAE83B5B',
#     'HOST-AEB2B5FAF15BD940',
#     'HOST-B718D533E78C3A4B',
#     'HOST-B849D719DC5E29DD',
#     'HOST-B9C77CCA36D90AFA',
#     'HOST-B9EC761559AE5400',
#     'HOST-BA2AD513B8334F48',
#     'HOST-BB40659229B3AA12',
#     'HOST-C1FD155279319956',
#     'HOST-C3CA6B8A251CE294',
#     'HOST-C40C28FB0A0F86C8',
#     'HOST-C55669ED81E7AF0F',
#     'HOST-C6678E7A75CD8985',
#     'HOST-C6C04B2A59EFB2E3',
#     'HOST-C7F8D672B4006BCB',
#     'HOST-C80170C737588F38',
#     'HOST-C819538EA2CDF1B3',
#     'HOST-C84FF2A36D206A81',
#     'HOST-CAD70926316C2F85',
#     'HOST-CBBDF6567FA193B3',
#     'HOST-CBDE295D785FA629',
#     'HOST-D0423BB6177B5D95',
#     'HOST-D05645957B9475F1',
#     'HOST-D444A0C6B7A0BB1B',
#     'HOST-D47186BA541085B5',
#     'HOST-D8D8A8660A1BBCE4',
#     'HOST-E02AD599FFCD2791',
#     'HOST-E40EB19359ACFCC2',
#     'HOST-E8B0FA9A542C6133',
#     'HOST-EA8E556D1CE28124',
#     'HOST-EB8921BD33565731',
#     'HOST-EFC311175A324027',
#     'HOST-F0450D943804CDC7',
#     'HOST-F2958527FD738B37',
#     'HOST-F336B5C12BA4255B',
#     'HOST-F4FAFCC592234A7F',
#     'HOST-F61F0EECE71C0DAB',
#     'HOST-F623DD3596C3E7A5',
#     'HOST-F6827D30240AC2BC',
#     'HOST-F9C51D589A986EF6',
#     'HOST-FA65A81E73F160CA',
#     'HOST-FBA425495DF2207B',
#     'HOST-FD7B2EAB4FBE5E0D',
# ]

# target_hosts = [
#     'HOST-863029D2471D4DD0',
#     'HOST-8066227A7020E61D',
# ]

target_hosts = [
    'HOST-1CC9F34AEF917C55',  # https://lcq01751.live.dynatrace.com/ui/settings/HOST-1CC9F34AEF917C55/builtin:host.monitoring?gtf=-2h&gf=all
    'HOST-8744FA8AC45BD857',  # https://lcq01751.live.dynatrace.com/ui/settings/HOST-8744FA8AC45BD857/builtin:host.monitoring?gtf=-2h&gf=all
    'HOST-C84FF2A36D206A81',  # https://lcq01751.live.dynatrace.com/ui/settings/HOST-C84FF2A36D206A81/builtin:host.monitoring?gtf=-2h&gf=all
    'HOST-25D8A6D8727DBAC8',  # https://lcq01751.live.dynatrace.com/ui/settings/HOST-25D8A6D8727DBAC8/builtin:host.monitoring?gtf=-2h&gf=all
]

friendly_function_name = 'Dynatrace Automation'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'Prep'
# env_name_supplied = 'Dev'
# env_name_supplied = 'Personal'
env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)


def process():
    for target_host in target_hosts:
        turn_on_infrastructure_only_monitoring(target_host)


'''
{
  "items": [
    {
      "objectId": "vu9U3hXa3q0AAAABABdidWlsdGluOmhvc3QubW9uaXRvcmluZwAESE9TVAAQODYzMDI5RDI0NzFENEREMAAkY2U1MDVlZjYtOWM1NC0zN2RjLWE2YTktZjlkNTFjOGYzNjdivu9U3hXa3q0",
      "value": {
        "enabled": true,
        "fullStack": true,
        "autoInjection": true
      }
    }
  ],
  "totalCount": 1,
  "pageSize": 100
}

{
  "value": {
    "autoMonitoring": true
  },
  "updateToken": "Y2ktaGdyb3VwLTEyMythZjhjOThlOS0wN2I0LTMyMGEtOTQzNi02NTEyMmVlNWY4NGQ=",
  "insertBefore": "Y2ktaGdyb3VwLTEyMythZjhjOThlOS0wN2I0LTMyMGEtOTQzNi02NTEyMmVlNWY4NGQ=",
  "schemaVersion": "1.0.0",
  "insertAfter": "Y2ktaGdyb3VwLTEyMythZjhjOThlOS0wN2I0LTMyMGEtOTQzNi02NTEyMmVlNWY4NGQ="
}
'''


def turn_on_infrastructure_only_monitoring(target_host):
    schema_id = 'builtin:host.monitoring'
    put_object_id_list = []
    post_payload_list = []

    endpoint = '/api/v2/settings/objects'
    params = 'schemaIds=' + urllib.parse.quote(schema_id) + '&scopes=' + target_host + '&fields=' + urllib.parse.quote('objectId,value')
    settings_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token, params=params)
    # print(settings_json_list)
    for settings_json in settings_json_list:
        total_count = settings_json.get('totalCount', '0')
        # print('total_count:', total_count)
        # print('total_count int:', int(total_count))
        if int(total_count) > 0:
            # print('total_count > 0')
            item_list = settings_json.get('items')
            for item in item_list:
                object_id = item.get('objectId')
                value = item.get('value')
                enabled = value.get('enabled', False)
                full_stack = value.get('fullStack', False)
                auto_injection = value.get('autoInjection', False)
                if enabled and full_stack and auto_injection:
                    # print('PUT ' + object_id)
                    put_object_id_list.append(object_id)
        else:
            # print('POST new object')
            payload_string = '{"schemaId": "' + schema_id + '", "scope": "' + target_host + '", "value": {"fullStack": false, "enabled": true, "autoInjection": true},"schemaVersion": "1.2"}'
            post_payload_list.append(json.loads(payload_string))

    if put_object_id_list:
        for put_object_id in put_object_id_list:
            payload_string = '{"value": {"fullStack": false, "enabled": true, "autoInjection": true}, "schemaVersion": "1.2"}'
            print('put', put_object_id, payload_string)
            dynatrace_api.put_object(f'{env}{endpoint}', token, put_object_id, json.dumps(payload_string))

    if post_payload_list:
        print('post', post_payload_list)
        dynatrace_api.post_object(f'{env}{endpoint}', token, json.dumps(post_payload_list))


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


if __name__ == '__main__':
    # For testing POST vs PUT you may want to delete an object ID
    # endpoint = '/api/v2/settings/objects'
    # dynatrace_api.delete_object(f'{env}{endpoint}, token, 'vu9U3hXa3q0AAAABACtidWlsdGluOmF2YWlsYWJpbGl0eS5wcm9jZXNzLWdyb3VwLWFsZXJ0aW5nAA1QUk9DRVNTX0dST1VQABAzRjQyODNBMDMwQ0I4Qjg0ACRhZjJlYWRiOS03YjY5LTNlODQtOTllOS03MDQxMzBiZDUwYTO-71TeFdrerQ')
    process()
