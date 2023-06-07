"""
Save synthetics from the tenant to the path indicated below.
"""
import json
import os
import re
import sys

from Reuse import dynatrace_api
from Reuse import environment


def save(path, file, content):
	if not os.path.isdir(path):
		os.makedirs(path)
	with open(path + "/" + file, "w", encoding='utf8') as text_file:
		text_file.write("%s" % json.dumps(content, indent=4))


def save_synthetics(env, token, path):
	download_count = 0
	r = dynatrace_api.get_object_list(env, token, endpoint='/api/v1/synthetic/monitors')
	res = r.json()
	print(res)
	for entry in res['monitors']:
		synthetic_name = entry.get('name')
		synthetic_id = entry.get('entityId')
		synthetic_type = entry.get('type')
		print(synthetic_name, synthetic_id, synthetic_type)
		if 'BRINK' in synthetic_name:
			synthetic = dynatrace_api.get_by_object_id(env, token, endpoint='/api/v1/synthetic/monitors', object_id=synthetic_id)
			if True:
				clean_filename = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", f'{synthetic_name}.json')
				print(f'Saving {synthetic_name} ({synthetic_id}) ({synthetic_type} type) to {clean_filename}')
				save(path, clean_filename, synthetic)
				download_count +=1

	print(f'Downloaded {download_count} synthetics to {path}')

def main():
	# env_name, env, token = environment.get_environment('Prod')
	# env_name, env, token = environment.get_environment('NonProd')
	# env_name, env, token = environment.get_environment('Prep')
	# env_name, env, token = environment.get_environment('Dev')
	env_name, env, token = environment.get_environment('Personal')
	# env_name, env, token = environment.get_environment('FreeTrial1')

	path = f'../../$Output/Tools/Synthetics/Downloads/{env_name}'
	print(f'Downloading synthetics for {env_name} to {path}')
	save_synthetics(env, token, path)


if __name__ == '__main__':
	main()
