import json

from Reuse import environment
from Reuse import new_platform_api


def process(env, client_id, client_secret):
	scope = 'storage:filter-segments:read storage:filter-segments:delete'

	oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)

	segment_name_dict = load_segment_names(env, oauth_bearer_token)

	params = {'page-size': 1000}
	results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/filter-segments/v1/filter-segments', params)
	segments_json = json.loads(results.text)
	segment_list = segments_json.get('filterSegments')

	count = 0
	delete_list = []

	for segment in segment_list:
		segment_uid = segment.get('uid')
		segment_name = segment.get('name')
		segment_owner = segment.get('owner')

		# if 'DeleteMe' in segment_name:
		# if segment_name == 'Template2':
		# if 'emplate' not in segment_name:
		if 'HG:' in segment_name:
			delete_list.append(f'{segment_uid}:{segment_name}:{segment_owner}')

	delete_list = sorted(delete_list)

	if len(delete_list) > 0:
		print('SEGMENTS TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = 'PROCEED WITH DELETE OF LISTED ENVIRONMENT-SHARES?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				line_split = line.split(':')
				segment_id = line_split[0]
				url = f'{env}/platform/storage/filter-segments/v1/filter-segments/{segment_id}'
				# print(url)
				response = new_platform_api.delete(oauth_bearer_token, url, None)
				if 200 < response.status_code < 300:
					print(f'DELETED: {line}', response.text, response.status_code, response.reason)
					count += 1
				else:
					print(f'DELETE FAILED: {line}', response.status_code, response.reason, response.text)

	print('Segments Deleted: ' + str(count))


def load_segment_names(env, oauth_bearer_token):
	segment_name_dict = {}
	params = {'page-size': 1000}
	results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/storage/filter-segments/v1/filter-segments', params)
	segments_json = json.loads(results.text)
	# print(segments_json)
	segment_list = segments_json.get('filterSegments')
	# print(segment_list)

	for segment in segment_list:
		segment_uid = segment.get('uid')
		segment_name = segment.get('name')
		segment_name_dict[segment_uid] = segment_name

	return segment_name_dict


def main():
	friendly_function_name = 'Dynatrace Automation'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, client_id, client_secret)


if __name__ == '__main__':
	main()
