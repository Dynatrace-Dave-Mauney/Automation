# import requests, ssl, os, sys, json, glob
import requests

from Reuse import dynatrace_api
from Reuse import environment


def delete(url, token, endpoint, params):
	full_url = url + endpoint
	resp = requests.delete(full_url, params=params, headers={'Authorization': "Api-Token " + token})
	# print(f'DELTE {full_url} {resp.status_code} - {resp.reason}')
	if resp.status_code != 204:
		print('REST API Call Failed!')
		print(f'DELETE {full_url} {params} {resp.status_code} - {resp.reason}')
		exit(1)


def process(env_name, env, token):
	print('Environment Name:' + env_name)
	print('Environment URL: ' + env)

	endpoint = '/api/config/v1/dashboards'
	params = ''
	dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)

	count = 0
	# delete_list = ['aaaaaaaa-bbbb-cccc-eeee-000000000000']
	delete_list = []

	for dashboards_json in dashboards_json_list:
		inner_dashboards_json_list = dashboards_json.get('dashboards')
		for inner_dashboards_json in inner_dashboards_json_list:
			dashboard_id = inner_dashboards_json.get('id')
			name = inner_dashboards_json.get('name')
			owner = inner_dashboards_json.get('owner')
			# print(dashboard_id, name, owner)

			# # # CAUTION HERE!!!! # # #
			# # # More flexible delete option is more dangerous! # # #
			# if owner.startswith('Dynatrace') and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-eeee-0000000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of 'Personal' environment
			# if 'TagReferenceCheck' in name or 'Dynatrace Resources' in name:
			# 	pass
			# else:
			# 	if owner == 'dave.mauney@dynatrace.com':
			# 		delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# # Full clean of 'DynatraceDashboardGenerator' dashboards
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-00000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of 'DynatraceDashboardGenerator' dashboards variant
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-10000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of 'AWS Supporting Services (Improved)' dashboards variant
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-eeee-f00000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of 'TEMP Detailed Drilldowns' dashboards variant
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-aaaa'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of certain 'BizOps' dashboards
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of original 'Kafka' dashboards
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-ffff-00000000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Full clean of certain generated dashboards
			# if owner == 'dave.mauney@dynatrace.com' and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-aaaa-00000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

	delete_list = sorted(delete_list)

	if len(delete_list) > 0:
		print('DASHBOARDS TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = 'PROCEED WITH DELETE OF LISTED DASHBOARDS?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				dashboard_id = line.split(':', 1)[0]
				endpoint = '/api/config/v1/dashboards/' + dashboard_id
				params = ''
				delete(env, token, endpoint, params)
				print('DELETED: ' + line)
				count += 1

	print('Dashboards Deleted: ' + str(count))


def run():
	# env_name, env, token = environment.get_environment('Prod')
	# env_name, env, token = environment.get_environment('Prep')
	# env_name, env, token = environment.get_environment('Dev')
	env_name, env, token = environment.get_environment('Personal')
	# env_name, env, token = environment.get_environment('FreeTrial1')
	process(env_name, env, token)


if __name__ == '__main__':
	run()
