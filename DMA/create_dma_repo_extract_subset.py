import json

from json import JSONDecodeError

INPUT_FILE_NAME = '$DMA_Repo_Extract.json'
# INPUT_FILE_NAME = '$DMA_Repo_Extract_EXAMPLE.json'
OUTPUT_FILE_NAME = '$DMA_Repo_Extract_Live_Buckets_ent_general.json'
OUTPUT_FILE_NAME = '$DMA_Repo_Extract_Live_Buckets_ent_os.json'
OUTPUT_FILE_NAME = '$DMA_Repo_Extract_Live_Buckets_app_general.json'

include_dashboards = True
include_notebooks = True

# include_dashboards = False
# include_notebooks = False

# ent_general bucket
subset_buckets = [
	'ent_general',
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
subset_buckets = [
	'ent_os',
	'app_li2196_main',
	'app_un1068_main',
	'app_vm1235_main',
	'app_wi2042_main',
	'app_zo0851_main',
]

# app_general bucket
subset_buckets = [
	'app_general',
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


def process():
	documents = create_dma_extract_subset()

	dma_extract = {
		'name': 'DMA Repo Extract Subset',
		'description': 'Subset of DMA Repo Documents extract of DQL/SPL and buckets for easier analysis and processing.',
		'documents': documents
	}

	output_json = json.dumps(dma_extract, indent=4, sort_keys=False)
	print(output_json)

	output_filename = OUTPUT_FILE_NAME
	with open(output_filename, 'w', encoding='utf-8') as outfile:
		outfile.write(output_json)


def create_dma_extract_subset():
	results = []
	with open(INPUT_FILE_NAME, 'r', encoding='utf-8') as f:
		infile_content = f.read()
	try:
		infile_content_json = json.loads(infile_content)
		documents = infile_content_json.get('documents')
		bucket_match = False
		for document in documents:
			document_name = document.get('document_name')
			document_type = document.get('document_type')
			if (document_type == 'dashboard' and include_dashboards) or (document_type == 'notebook' and include_notebooks):
				document_items = document.get('document_items')
				for document_item in document_items:
					bucket = document_item.get('bucket')
					if bucket in subset_buckets:
						print(f'Bucket {bucket} in {document_name}')
						bucket_match = True
				if bucket_match:
					# For testing
					# pass
					results.append(document)
	except JSONDecodeError:
		print(f'Skipping due to non-JSON file content: {INPUT_FILE_NAME}')

	return results


if __name__ == '__main__':
	process()
