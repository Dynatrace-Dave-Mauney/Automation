import json

from Reuse import environment
from Reuse import new_platform_api


def process(env, client_id, client_secret):
	scope = 'document:documents:read document:documents:delete'

	oauth_bearer_token = new_platform_api.get_oauth_bearer_token(client_id, client_secret, scope)
	params = {'page-size': 1000}
	results = new_platform_api.get(oauth_bearer_token, f'{env}/platform/document/v1/documents', params)
	documents_json = json.loads(results.text)
	document_list = documents_json.get('documents')

	count = 0
	# delete_list = ['f0c29915-7717-4afd-9ed0-a6031fa670cd']
	delete_list = []

	for document in document_list:
		document_type = document.get('type')
		if document_type == 'dashboard':
			document_id = document.get('id')
			document_name = document.get('name')
			document_version = document.get('version')
			delete_list.append(f'{document_name}:{document_id}:{document_version}')

	delete_list = sorted(delete_list)

	if len(delete_list) > 0:
		print('DASHBOARDS TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = 'PROCEED WITH DELETE OF LISTED DASHBOARDS?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				line_split = line.split(':')
				dashboard_id = line_split[1]
				dashboard_version = line_split[2]
				params = f'optimistic-locking-version={dashboard_version}'
				response = new_platform_api.delete(oauth_bearer_token, f'{env}/platform/document/v1/documents/{dashboard_id}', params)
				if 200 < response.status_code < 300:
					print(f'DELETED: {line}', response.text, response.status_code, response.reason)
					count += 1
				else:
					print(f'DELETE FAILED: {line}', response.status_code, response.reason, response.text)

	print('Dashboards Deleted: ' + str(count))


def main():
	friendly_function_name = 'Dynatrace Platform Document'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, client_id, client_secret = environment.get_client_environment_for_function(env_name_supplied, friendly_function_name)
	process(env, client_id, client_secret)


if __name__ == '__main__':
	main()
