"""
Save synthetics from the tenant to the path indicated below.
"""
import json
import os
import re

from Reuse import dynatrace_api
from Reuse import environment


def save(path, file, content):
	if not os.path.isdir(path):
		os.makedirs(path)
	with open(path + "/" + file, "w", encoding='utf8') as text_file:
		text_file.write("%s" % json.dumps(content, indent=4))


def save_synthetics(env, token, path):
	endpoint = '/api/v1/synthetic/monitors'
	download_count = 0
	r = dynatrace_api.get_without_pagination(f'{env}{endpoint}', token)
	res = r.json()
	print(res)
	for entry in res['monitors']:
		synthetic_name = entry.get('name')
		synthetic_id = entry.get('entityId')
		synthetic_type = entry.get('type')
		print(synthetic_name, synthetic_id, synthetic_type)
		# if 'BRINK' in synthetic_name:
		if True:
			endpoint = '/api/v1/synthetic/monitors'
			r = dynatrace_api.get_without_pagination(f'{env}{endpoint}/{synthetic_id}', token)
			synthetic = r.json()
			if True:
				clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{synthetic_name}.json')
				print(f'Saving {synthetic_name} ({synthetic_id}) ({synthetic_type} type) to {clean_filename}')
				save(path, clean_filename, synthetic)
				download_count += 1

	print(f'Downloaded {download_count} synthetics to {path}')


def main():
	friendly_function_name = 'Dynatrace Automation Tools'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

	path = f'../../$Output/Tools/Synthetics/Downloads/{env_name}'
	print(f'Downloading synthetics for {env_name} to {path}')
	save_synthetics(env, token, path)


if __name__ == '__main__':
	main()
