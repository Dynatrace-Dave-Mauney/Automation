import json

from Reuse import environment
from Reuse import new_platform_api


def process(env, client_id, client_secret):
	scope = 'document:environment-shares:read document:environment-shares:delete'

	oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
	params = {'page-size': 1000}
	results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares', params)
	environment_shares_json = json.loads(results.text)
	environment_share_list = environment_shares_json.get('environment-shares')

	count = 0
	delete_list = []

	for environment_share in environment_share_list:
		environment_share_id = environment_share.get('id')
		environment_share_document_id = environment_share.get('documentId')
		environment_share_access = environment_share.get('access')
		environment_share_claim_count = environment_share.get('claimCount')
		delete_list.append(f'{environment_share_id}:{environment_share_document_id}:{environment_share_access}:{environment_share_claim_count}')

	delete_list = sorted(delete_list)

	if len(delete_list) > 0:
		print('ENVIRONMENT-SHARES TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = 'PROCEED WITH DELETE OF LISTED ENVIRONMENT-SHARES?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				line_split = line.split(':')
				environment_share_id = line_split[0]
				response = new_platform_api.delete(oauth_bearer_token, f'{env}/platform/document/v1/environment-shares/{environment_share_id}', None)
				if 200 < response.status_code < 300:
					print(f'DELETED: {line}', response.text, response.status_code, response.reason)
					count += 1
				else:
					print(f'DELETE FAILED: {line}', response.status_code, response.reason, response.text)

	print('Environment Shares Deleted: ' + str(count))


def main():
	friendly_function_name = 'Dynatrace Platform Document'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'Prep'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'FreeTrial1'
	env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, client_id, client_secret)


if __name__ == '__main__':
	main()
