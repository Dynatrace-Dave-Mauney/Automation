import copy
import os

# Remove various prefixes from DMA Repo document metadata files
DASHBOARD_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Dashboards'
NOTEBOOK_REPO_PATH = '../$Private/Customers/$Current/DMA/Repo/Notebooks'

replacements = [
    # See repair_names_in_metadata.py for example
]

# ent_general bucket
convert_to_ent_general = [
    'app_ai4575_main',
    'app_al3576_main',
    'app_am4659_main',
    'app_an2873_main',
    'app_at4349_main',
    'app_bi2663_main',
    'app_bu1894_main',
    'app_bu4467_main',
    'app_ch4357_main',
    'app_ci4712_main',
    'app_ci5017_main',
    'app_co2159_main',
    'app_co3698_main',
    'app_co4175_main',
    'app_da2131_main',
    'app_da3646_main',
    'app_da3788_main',
    'app_db1076_main',
    'app_db4154_main',
    'app_de4952_main',
    'app_ec1309_main',
    'app_ec4704_main',
    'app_el4199_main',
    'app_en1981_main',
    'app_fi1770_main',
    'app_ge4961_main',
    'app_gi2690_main',
    'app_gi4260_main',
    'app_it3697_main',
    'app_it3710_main',
    'app_je2700_main',
    'app_je3689_main',
    'app_ms3651_main',
    'app_na4874_main',
    'app_ne1699_main',
    'app_ni3537_main',
    'app_of3086_main',
    'app_op4348_main',
    'app_or0566_main',
    'app_or3704_main',
    'app_po3012_main',
    'app_ra3669_main',
    'app_re2695_main',
    'app_re4368_main',
    'app_sa3825_main',
    'app_si0083_main',
    'app_sn3538_main',
    'app_sw3662_main',
    'app_sy3937_main',
    'app_te4016_main',
    'app_ti1878_main',
    'app_ui4504_main',
    'app_xm4899_main',
    'grp_enablingtech_main',
    'grp_storage_main',
]

# ent_os bucket
convert_to_ent_os = [
    'app_li2196_main',
    'app_un1068_main',
    'app_vm1235_main',
    'app_wi2042_main',
    'app_zo0851_main',
]

# app_general bucket
convert_to_app_general = [
    'app_mo5029_main',
    'app_na3974_main',
    'app_na5189_main',
    'app_nc0619_main',
    'app_nc3849_main',
    'app_ne4311_main',
    'app_ne4446_main',
    'app_of2836_main',
    'app_of4305_main',
    'app_of5019_main',
    'app_on1048_main',
    'app_op0842_main',
    'app_op1445_main',
    'app_op1753_main',
    'app_or4189_main',
    'app_oz3046_main',
    'app_pi4630_main',
    'app_pi4643_main',
    'app_pi4877_main',
    'app_ra1771_main',
    'app_re2015_main',
    'app_re2691_main',
    'app_re3779_main',
    'app_re3868_main',
    'app_re4818_main',
    'app_ri4170_main',
    'app_rm2351_main',
    'app_rs1500_main',
    'app_rs1848_main',
    'app_rs3685_main',
    'app_rs5083_main',
    'app_sa4869_main',
    'app_se4754_main',
    'app_si4161_main',
    'app_sw4658_main',
    'app_sw4810_main',
    'app_sy4925_main',
    'app_te5010_main',
    'app_th4359_main',
    'app_tm1827_main',
    'app_to5134_main',
    'app_un4216_main',
    'app_un4835_main',
    'app_va1714_main',
    'app_vc4687_main',
    'app_ve4309_main',
    'app_ve5080_main',
    'app_vi4229_main',
    'app_wi0118_main',
]


def main():
    try:
        input_directory_names = [DASHBOARD_REPO_PATH, NOTEBOOK_REPO_PATH]

        for input_directory_name in input_directory_names:
            #
            # input_directory_name = DASHBOARD_REPO_PATH
            # input_directory_name = NOTEBOOK_REPO_PATH
            output_directory_name = input_directory_name + '-MODIFIED'

            print(f'Converting bucket names in {input_directory_name} to {output_directory_name}')

            for file_name in os.listdir(input_directory_name):
                if os.path.isfile(f'{input_directory_name}/{file_name}') and file_name.endswith('.json') and '.metadata.' not in file_name:
                    src = f'{input_directory_name}/{file_name}'
                    dst = f'{output_directory_name}/{file_name}'
                    # print(f'Source: {src} Destination: {dst}')

                    with open(src, 'r', encoding='utf-8') as infile:
                        new_string = infile.read()
                        original_string = copy.deepcopy(new_string)

                        for replacement in replacements:
                            # Normal order
                            from_string, to_string = replacement
                            # Reversal order
                            # to_string, from_string = replacement
                            new_string = new_string.replace(from_string, to_string)

                        for index in convert_to_ent_general:
                            from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                            to_bucket_filter = 'bucket: {\\"ent_general\\"}'
                            if from_bucket_filter in new_string:
                                new_string = new_string.replace(from_bucket_filter, to_bucket_filter)
                                # print('ent_general:', from_bucket_filter, to_bucket_filter, new_string)

                        for index in convert_to_app_general:
                            from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                            to_bucket_filter = 'bucket: {\\"app_general\\"}'
                            if from_bucket_filter in new_string:
                                new_string = new_string.replace(from_bucket_filter, to_bucket_filter)
                                # print('app_general:', from_bucket_filter, to_bucket_filter, new_string)

                        for index in convert_to_ent_os:
                            from_bucket_filter = 'bucket: {\\"' + index + '\\"}'
                            to_bucket_filter = 'bucket: {\\"ent_os\\"}'
                            if from_bucket_filter in new_string:
                                new_string = new_string.replace(from_bucket_filter, to_bucket_filter)
                                # print('ent_os:', from_bucket_filter, to_bucket_filter, new_string)

                        if new_string != original_string:
                            print(f'Changed {original_string} to {new_string} for {dst}')
                            with open(dst, 'w', encoding='utf-8') as outfile:
                                outfile.write(new_string)
    except FileNotFoundError:
        print('The directory name does not exist')


if __name__ == '__main__':
    main()
