# Replace strings in all/selected files in a directory and optionally rename the files

# Customer 2 (Non-Prod)
# replacements = [
#     ('00000000-dddd-bbbb-ffff-000000000001', 'bf78a5a2-9cf5-4937-a691-74b3fdf90f27'),
#     ('00000000-dddd-bbbb-ffff-000000000002', '5384cc39-fd54-47aa-9ae9-e62d43696bb4'),
#     ('00000000-dddd-bbbb-ffff-000000000003', '9296ad4d-ce99-46f2-8d07-893dbe55c206'),
#     ('00000000-dddd-bbbb-ffff-000000000004', 'db1f67eb-7c3c-4eeb-96fd-17fe07f2d2bf'),
#     ('00000000-dddd-bbbb-ffff-000000000005', '733d90c3-fd30-4353-aef8-cffcfb480aa7'),
#     ('00000000-dddd-bbbb-ffff-000000000006', '1685384b-3a28-4b69-b63f-01accafe5094'),
#     ('00000000-dddd-bbbb-ffff-000000000007', '89716753-1f27-4237-a0b6-c15f4e921303'),
#     ('00000000-dddd-bbbb-ffff-000000000008', 'b04de2aa-0d35-4608-9880-dcb042c9ec3e'),
#     ('00000000-dddd-bbbb-ffff-000000000009', '4df3fbd6-b410-4fcf-b0f5-7e9d5cdd11eb'),
#     ('00000000-dddd-bbbb-ffff-000000000010', 'a991edd1-6f7b-4382-bf3c-afbd55b3eee8'),
#     ('00000000-dddd-bbbb-ffff-000000000011', '14f35d47-4a10-4fcf-a6cb-ace26642723d'),
#     ('00000000-dddd-bbbb-ffff-000000000012', 'c16a4a36-9cf7-4614-b28c-4d0dcdc38ef1'),
#     ('00000000-dddd-bbbb-ffff-000000000013', 'e44e4dce-23c6-431a-ae30-7b4ba4082eac'),
#     ('00000000-dddd-bbbb-ffff-000000000014', '7b773b39-d973-41c0-a186-96d68f432fdf'),
#     ('00000000-dddd-bbbb-ffff-000000000017', '1a22b7d2-b936-47e1-ae15-9d2f43743e2d'),
#     ('00000000-dddd-bbbb-ffff-000000000018', '98df1759-ce62-481f-876a-28992fbe70b6'),
#     ('00000000-dddd-bbbb-ffff-000000000019', '3e62b122-a0ce-4224-9bba-5b7e5f26acd3'),
#     ('00000000-dddd-bbbb-ffff-000000000020', '7357c7dd-2637-491d-a60a-92b05eec6f63'),
#     ('00000000-dddd-bbbb-ffff-000000000021', '6229788b-903a-49b7-8420-a954d53b34d5'),
#     ('00000000-dddd-bbbb-ffff-000000000029', '35143e9e-b95c-4e41-a012-cc607d610fb4'),
#     ('00000000-dddd-bbbb-ffff-000000000030', '5036f0d4-db68-48a5-af63-fc79b82c8350'),
#     ('00000000-dddd-bbbb-ffff-000000000040', '6db488c2-0a7c-4982-aa6b-5788067f7f2b'),
#     ('00000000-dddd-bbbb-ffff-000000000041', 'a3154377-df77-4dc4-b52d-c00643289a06'),
#     ('00000000-dddd-bbbb-ffff-000000000042', '6bd3a2e0-9925-44f3-aee3-3ce1fbd2aa35'),
#     ('00000000-dddd-bbbb-ffff-000000000043', 'e474cac7-58a7-4417-b75b-8961738fc567'),
#     ('00000000-dddd-bbbb-ffff-000000000044', 'b3a1d16d-7910-41b8-adfe-52bd5eb402d1'),
#     ('00000000-dddd-bbbb-ffff-000000000045', 'e3be77bf-6d82-4707-a0c7-4ed16165bb2d'),
#     ('00000000-dddd-bbbb-ffff-000000000047', 'cc924f0f-d496-48c4-9f6d-da36a889c496'),
#     ('00000000-dddd-bbbb-ffff-000000000100', '7cc72da9-f1ca-4529-9499-a94d391aac7c'),
#     ('00000000-dddd-bbbb-ffff-000000000101', 'f05d4cdd-b7cb-43e8-ab61-793dde43256d'),
#     ('00000000-dddd-bbbb-ffff-000000000102', '9afdcbde-9541-41a2-9000-2fc11e988521'),
#     ('00000000-dddd-bbbb-ffff-000000000800', '262d4034-fcf7-40c9-9385-5a2c2c556adf'),
#     ('00000000-dddd-bbbb-ffff-000000000801', '2d60b775-af56-482b-96aa-1631b44b45a3'),
#     ('00000000-dddd-bbbb-ffff-000000000802', '20ff6e4d-c0b2-457b-8e0c-3d993becb93f'),
#     ('00000000-dddd-bbbb-ffff-000000000803', 'b0b2d7b8-7bd5-4798-b758-b173096428f0'),
#     ('00000000-dddd-bbbb-ffff-000000000804', 'f15209cf-fde8-41d0-9b08-f18a8e1dde07'),
#     ('00000000-dddd-bbbb-ffff-000000000805', '4b623799-ab1f-49cd-b74c-790378f37daa'),
#     ('00000000-dddd-bbbb-ffff-000000000806', '7188d2b1-b8c3-416f-80e6-149707588182'),
#     ('00000000-dddd-bbbb-ffff-000000000807', 'c4d447e5-cf7e-4b1a-9931-32953d2c5db4'),
#     ('00000000-dddd-bbbb-ffff-000000000808', '81c3a1ca-1d9b-493a-8b16-114de260cb66'),
#     ('00000000-dddd-bbbb-ffff-000000000900', '2747ba89-7c46-4927-a7b4-7307bf41210b'),
# ]
#
# Customer 2 (Prod)
replacements = [
    ('00000000-dddd-bbbb-ffff-000000000001', '54e1fd8d-25b0-42d4-9465-fb6c118a2c43'),
    ('00000000-dddd-bbbb-ffff-000000000002', '4c2daed8-d8a8-4d7a-ad04-454e0e5b8916'),
    ('00000000-dddd-bbbb-ffff-000000000003', '83d4d6fd-1205-47a3-88e5-3c606baf6b22'),
    ('00000000-dddd-bbbb-ffff-000000000004', '849f0ef1-3577-46e3-9810-346470c01f26'),
    ('00000000-dddd-bbbb-ffff-000000000005', 'bfaa210f-0348-4756-8ca8-84769c89a994'),
    ('00000000-dddd-bbbb-ffff-000000000006', 'cd0423a5-2bbe-476b-8512-8290581348f9'),
    ('00000000-dddd-bbbb-ffff-000000000007', '0f18ceb9-12d0-4081-b494-55165aed881f'),
    ('00000000-dddd-bbbb-ffff-000000000008', '0887792f-7475-4afd-acd9-979e4c4e634e'),
    ('00000000-dddd-bbbb-ffff-000000000009', 'b67ed4cf-bb6e-45ca-9ca5-1337a7e1fb03'),
    ('00000000-dddd-bbbb-ffff-000000000010', '93d527e4-b1f5-406a-b425-23e3c2d60bdc'),
    ('00000000-dddd-bbbb-ffff-000000000011', '8f3ba6a0-cab8-42fb-a242-808daf86db68'),
    ('00000000-dddd-bbbb-ffff-000000000012', 'efbf23d2-6749-4495-b137-ffa4b38872e1'),
    ('00000000-dddd-bbbb-ffff-000000000013', '863d52e4-b8b3-4927-ae7d-70e6e02bc58d'),
    ('00000000-dddd-bbbb-ffff-000000000014', '547c6c40-d41c-4c40-a8b9-c82ceda4b73e'),
    ('00000000-dddd-bbbb-ffff-000000000017', 'b3a4caa8-926b-4144-a8bf-fec04fc697b8'),
    ('00000000-dddd-bbbb-ffff-000000000018', '52533c00-b7a8-456a-862a-c46d49327e0e'),
    ('00000000-dddd-bbbb-ffff-000000000019', '259da4db-99db-4ab0-b228-ddb88d2a5b67'),
    ('00000000-dddd-bbbb-ffff-000000000020', 'e5a1f75e-4a5c-44ef-91d1-6b9740a79001'),
    ('00000000-dddd-bbbb-ffff-000000000021', '92b4a5f2-2ebc-44e8-8fc5-bd3e6a36e0e4'),
    ('00000000-dddd-bbbb-ffff-000000000029', '08b88ece-d180-45ed-9f3d-d933fb108de3'),
    ('00000000-dddd-bbbb-ffff-000000000030', 'c5d6df6b-a712-4395-abf8-1565d9a53ed8'),
    ('00000000-dddd-bbbb-ffff-000000000040', '6df19bc6-3c80-4201-b211-f0f2a1dcdecc'),
    ('00000000-dddd-bbbb-ffff-000000000041', '2c4ccb81-2936-4699-822a-1414128eebc0'),
    ('00000000-dddd-bbbb-ffff-000000000042', '5c649e31-4ab9-47bb-991c-fa0bcd0364d9'),
    ('00000000-dddd-bbbb-ffff-000000000043', 'f188e3ed-9cae-45f3-bdd5-81fb97268cd4'),
    ('00000000-dddd-bbbb-ffff-000000000044', 'f6870927-805c-42d3-9896-0242c94cf2a8'),
    ('00000000-dddd-bbbb-ffff-000000000045', '80f8c4be-8f23-493b-b7dd-8f74505378dc'),
    ('00000000-dddd-bbbb-ffff-000000000047', '15a10a96-edac-4af9-b112-8e1e6fa29145'),
    ('00000000-dddd-bbbb-ffff-000000000067', 'ca95330a-b257-4cbe-844c-9db4ab692ed2'),
    ('00000000-dddd-bbbb-ffff-000000000068', '4d7e2e76-4197-4b1b-b4f8-337f38cbe93c'),
    ('00000000-dddd-bbbb-ffff-000000000069', 'a5ac7e58-1934-402e-aa94-3faef01ff95e'),
    ('00000000-dddd-bbbb-ffff-000000000070', 'e3175df6-ef65-40c5-94f3-f48b13135bc8'),
    ('00000000-dddd-bbbb-ffff-000000000071', 'e85be585-022a-4356-b939-87b6edb09461'),
    ('00000000-dddd-bbbb-ffff-000000000072', 'b64d602c-d0ed-4611-9edf-e1775e793a61'),
    ('00000000-dddd-bbbb-ffff-000000000073', '74a23eb6-93f1-432b-9338-28aa0079f569'),
    ('00000000-dddd-bbbb-ffff-000000000074', '723eb93b-9d8b-4296-9bbd-1787a36469d4'),
    ('00000000-dddd-bbbb-ffff-000000000100', 'f5e7e9a4-c128-40bc-8c07-2e6d673f1d44'),
    ('00000000-dddd-bbbb-ffff-000000000101', 'ba5d8c37-98b3-4f1d-9f26-28d23a575fc8'),
    ('00000000-dddd-bbbb-ffff-000000000102', 'fa5ac562-6309-4b88-a583-d0c2e7b7aaa4'),
    ('00000000-dddd-bbbb-ffff-000000000103', 'aad9b88f-52dd-4312-9b2d-e0de2744333'),
    ('00000000-dddd-bbbb-ffff-000000000104', 'd0ccac7d-fbdf-412f-a781-1976ce0767dc'),
    ('00000000-dddd-bbbb-ffff-000000000110', 'e89b4256-f6e5-451b-9fec-9dfa42556310'),
    ('00000000-dddd-bbbb-ffff-000000000111', '453c939f-3d95-46fe-9888-8f6e36dbee1a'),
    ('00000000-dddd-bbbb-ffff-000000000075', '5a3d7022-7fa7-44c8-8952-8e11f13e92c3'),
    ('00000000-dddd-bbbb-ffff-000000000120', 'd061a5ca-c735-4da0-bae4-e90425cc7b2b'),
    ('00000000-dddd-bbbb-ffff-000000000121', '2da327db-c8ab-4a38-bc3c-d84b421a20dd'),
    ('00000000-dddd-bbbb-ffff-000000000800', 'f9d0aaae-135e-49b7-9dc5-67ab79b12cc6'),
    ('00000000-dddd-bbbb-ffff-000000000801', '3b643415-86cf-4964-8c09-17039d02afc3'),
    ('00000000-dddd-bbbb-ffff-000000000802', 'bc09871f-7ea4-434b-8350-669ba7b583a8'),
    ('00000000-dddd-bbbb-ffff-000000000803', '5534e91b-7021-4dc1-9b43-02084e97e905'),
    ('00000000-dddd-bbbb-ffff-000000000804', 'd5acac88-a39c-43d5-b949-d7b8a469922e'),
    ('00000000-dddd-bbbb-ffff-000000000805', '0635bf20-269c-4855-924d-20ab21171889'),
    ('00000000-dddd-bbbb-ffff-000000000806', 'ce188e65-f8fc-48c9-b0a9-0731622d3bb2'),
    ('00000000-dddd-bbbb-ffff-000000000807', '663a369b-79cb-4d91-ae71-43f9ee3b8edd'),
    ('00000000-dddd-bbbb-ffff-000000000808', '09fe94ec-3ef5-4614-9034-c6b0a510eca8'),
    ('00000000-dddd-bbbb-ffff-000000000809', 'ba657ad8-9d9f-46b9-8705-98ff143ad8f0'),
    ('00000000-dddd-bbbb-ffff-000000000900', '68be9a5e-f7d9-4e63-85bb-231d9d9d8ebe'),
]

# DEMO
# replacements = [
#     ('00000000-dddd-bbbb-ffff-000000000001', '3b2675c0-c46d-4977-abe2-b986273f040e'),
#     ('00000000-dddd-bbbb-ffff-000000000002', 'de949708-8a68-4a74-93d3-d0ce9ccf5bf7'),
#     ('00000000-dddd-bbbb-ffff-000000000003', 'ad5d61c7-1530-4038-8402-cb6050247bdb'),
#     ('00000000-dddd-bbbb-ffff-000000000004', 'e9e57c11-e117-4822-ad04-f3fea0987a52'),
#     ('00000000-dddd-bbbb-ffff-000000000005', '6935d45b-1822-493d-bc41-cdf43888e67b'),
#     ('00000000-dddd-bbbb-ffff-000000000006', '7c2cde74-8922-4eca-aef9-90b12bd728f1'),
#     ('00000000-dddd-bbbb-ffff-000000000007', '8c028f2d-aa71-4926-84d8-186a3c3fd20e'),
#     ('00000000-dddd-bbbb-ffff-000000000008', '7e7f3ae5-a10a-4c57-814f-89dbda344870'),
#     ('00000000-dddd-bbbb-ffff-000000000009', '8a615cd0-910f-4fbf-9dcd-35803de09ede'),
#     ('00000000-dddd-bbbb-ffff-000000000010', 'e7a3a05b-b0f5-49b2-bd61-bd58f1722126'),
#     ('00000000-dddd-bbbb-ffff-000000000011', '9f665a9b-6578-4a52-9d9a-c96ac9d17c18'),
#     ('00000000-dddd-bbbb-ffff-000000000012', 'ee2bf4c8-7a32-4cb2-833c-ec7f8f72fd03'),
#     ('00000000-dddd-bbbb-ffff-000000000013', '0650f78d-36b9-463b-8bd5-069c9269cfeb'),
#     ('00000000-dddd-bbbb-ffff-000000000014', '716c67d9-2933-401d-8303-2952661eefe3'),
#     ('00000000-dddd-bbbb-ffff-000000000015', 'e677ba89-f7f8-45d1-99d1-d2e6a5b30ab9'),
#     ('00000000-dddd-bbbb-ffff-000000000016', '3e7ff370-7ce9-43ad-b938-d8ec6758c23b'),
#     ('00000000-dddd-bbbb-ffff-000000000017', '84d300a2-5265-4d22-a6b7-aa03cff4848d'),
#     ('00000000-dddd-bbbb-ffff-000000000018', '8b06b224-c8ee-405b-a88d-4e5af81de1e9'),
#     ('00000000-dddd-bbbb-ffff-000000000019', '4615bb9e-c2fb-4274-a783-53435b8e4e44'),
#     ('00000000-dddd-bbbb-ffff-000000000020', 'e22fdd80-b735-4e6e-a133-16a01a74c590'),
#     ('00000000-dddd-bbbb-ffff-000000000021', '17898e63-c4cb-4943-bb74-4a111dda6370'),
#     ('00000000-dddd-bbbb-ffff-000000000040', '3b782608-f7cd-4133-becb-9565e1a8f910'),
#     ('00000000-dddd-bbbb-ffff-000000000041', 'fa6b7f83-79be-4f30-8daa-a8de272d888b'),
#     ('00000000-dddd-bbbb-ffff-000000000042', '16da2239-5495-4c99-9963-fe501d37acce'),
#     ('00000000-dddd-bbbb-ffff-000000000043', 'c29083c6-0433-4869-a15c-05fa48d26eb6'),
#     ('00000000-dddd-bbbb-ffff-000000000044', '5342296d-f9ec-4030-a4eb-003de8ff7aa6'),
#     ('00000000-dddd-bbbb-ffff-000000000045', 'c8bab890-f371-4dae-90af-406f2fd474f3'),
#     ('00000000-dddd-bbbb-ffff-000000000047', 'fe6b093e-0dec-4920-a09d-720652a98f21'),
#     ('00000000-dddd-bbbb-ffff-000000000060', 'e201c09d-7c0c-4418-94ca-eeb62f6fe671'),
#     ('00000000-dddd-bbbb-ffff-000000000061', '91ca692e-896c-46bf-bb9d-0480b61f6f74'),
#     ('00000000-dddd-bbbb-ffff-000000000062', 'd19e063a-2c25-45e4-91b6-524b5acb41ca'),
#     ('00000000-dddd-bbbb-ffff-000000000063', '37b8d250-dc96-46a6-ac8c-a62b0223fc7b'),
#     ('00000000-dddd-bbbb-ffff-000000000064', '34ad309c-44f2-47ea-8636-a40e4c1f19a5'),
#     ('00000000-dddd-bbbb-ffff-000000000065', '84ceb827-0cd0-4204-87c6-57ffef41459c'),
#     ('00000000-dddd-bbbb-ffff-000000000066', 'd6b7db1d-3a95-408b-b903-3a9e002fa891'),
#     ('00000000-dddd-bbbb-ffff-000000000100', '9e68f210-c352-4c04-b92d-82156566c693'),
#     ('00000000-dddd-bbbb-ffff-000000000101', '08799bab-63ed-4b33-b562-4a73c4fd347d'),
#     ('00000000-dddd-bbbb-ffff-000000000102', '291ad65a-5449-4cf5-815b-56ba1017e057'),
#     ('00000000-dddd-bbbb-ffff-000000000800', 'bad2112f-98b9-4e8e-bd46-c00f5df21726'),
#     ('00000000-dddd-bbbb-ffff-000000000801', 'ede07662-3b60-4123-abbc-ad8d56c9f983'),
#     ('00000000-dddd-bbbb-ffff-000000000802', 'b68b6948-96ce-4acd-b757-878f7c97005c'),
#     ('00000000-dddd-bbbb-ffff-000000000803', '6719987d-b8d5-49c4-ad74-c861fc47db1f'),
#     ('00000000-dddd-bbbb-ffff-000000000804', 'cbf80726-5028-479f-b2dc-19ad08f6e710'),
#     ('00000000-dddd-bbbb-ffff-000000000805', 'cb7deb71-3273-4a25-bda8-2f320a4b7b87'),
#     ('00000000-dddd-bbbb-ffff-000000000806', 'fb0974b0-0e0c-4b23-9912-631ace872751'),
#     ('00000000-dddd-bbbb-ffff-000000000807', '587c0b6d-a9cd-4d3b-b448-dbba94bce825'),
#     ('00000000-dddd-bbbb-ffff-000000000808', 'bf1c5a69-ff4d-4353-9478-d16ee78a8248'),
#     ('00000000-dddd-bbbb-ffff-000000000900', 'dbff69b1-8c3f-4fb3-a348-390b3297f2ac'),
#     ('aaaaaaaa-0001-0001-0001-000000000001', 'ede07662-3b60-4123-abbc-ad8d56c9f983'),
#     ('aaaaaaaa-0001-0001-0001-000000000002', 'b68b6948-96ce-4acd-b757-878f7c97005c'),
#     ('aaaaaaaa-0001-0001-0001-000000000003', '6719987d-b8d5-49c4-ad74-c861fc47db1f'),
#     ('aaaaaaaa-0001-0001-0001-000000000004', 'cbf80726-5028-479f-b2dc-19ad08f6e710'),
# ]

import os

def main():
    try:
        input_directory_name = "../../Dashboards/Templates/Overview"
        output_directory_name = '../../Dashboards/Templates/Overview-Customer2-NonProd-Reversed'
        # output_directory_name = '../../Dashboards/Templates/Overview-Demo'
        # output_directory_name = '../../Dashboards/Templates/Overview-Customer2-NonProd'
        # output_directory_name = '../../Dashboards/Templates/Overview-Customer2-Prod'

        for file_name in os.listdir(input_directory_name):
            # if os.path.isfile(f'{input_directory_name}/{file_name}') and file_name.startswith('00000000-') and file_name.endswith('.json'):
            if os.path.isfile(f'{input_directory_name}/{file_name}') and file_name == '00000000-dddd-bbbb-ffff-000000000001-v2.json':
                src = f'{input_directory_name}/{file_name}'
                dst = f'{output_directory_name}/{file_name}'

                with open(src, 'r', encoding='utf-8') as infile:
                    new_string = infile.read()
                    for replacement in replacements:
                        # Normal order
                        from_string, to_string = replacement
                        # Reversal order
                        to_string, from_string = replacement
                        new_string = new_string.replace(from_string, to_string)
                    print(f'{src} {dst} {from_string} {to_string}')
                    with open(dst, 'w', encoding='utf-8') as outfile:
                        outfile.write(new_string)

    except FileNotFoundError:
        print('The directory name does not exist')




if __name__ == '__main__':
    main()
