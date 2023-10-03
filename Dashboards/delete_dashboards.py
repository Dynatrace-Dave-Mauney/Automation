from Reuse import dynatrace_api
from Reuse import environment


def process(env_name, env, token):
	print('Environment Name:' + env_name)
	print('Environment URL: ' + env)

	endpoint = '/api/config/v1/dashboards'
	params = ''
	dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)

	count = 0
	# delete_list = ['f0c29915-7717-4afd-9ed0-a6031fa670cd']
	delete_list = []

	for dashboards_json in dashboards_json_list:
		inner_dashboards_json_list = dashboards_json.get('dashboards')
		for inner_dashboards_json in inner_dashboards_json_list:
			dashboard_id = inner_dashboards_json.get('id')
			name = inner_dashboards_json.get('name')
			owner = inner_dashboards_json.get('owner')
			# print(dashboard_id, name, owner)

			# # # CAUTION HERE!!!! # # #
			# # # More flexible delete options are more dangerous! # # #
			# if owner.startswith('Dynatrace') and dashboard_id.startswith('aaaaaaaa-bbbb-cccc-eeee-0000000000'):
			# 	delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

			# Clean of 'Prod' environment
			# if owner == 'dave.mauney@dynatrace.com':
			if 'mauney' in owner.lower():
				# print(name)
				# if dashboard_id.startswith('aaaaaaaa'):
				# if name.endswith('-PROD SLOs'):
				# if 'SQL Server' in name and not dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000'):
				# if not name.startswith('Prod:') and not name.startswith('TEMP:'):
				if dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-'):
					delete_list.append(dashboard_id + ': ' + name + ': ' + owner)

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
				dynatrace_api.delete(env, token, endpoint, params)
				print('DELETED: ' + line)
				count += 1

	print('Dashboards Deleted: ' + str(count))


def run():
	friendly_function_name = 'Dynatrace Automation'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	# env_name_supplied = 'Prod'
	# env_name_supplied = 'NonProd'
	# env_name_supplied = 'Prep'
	# env_name_supplied = 'Dev'
	# env_name_supplied = 'Personal'
	# env_name_supplied = 'Demo'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env_name, env, token)


if __name__ == '__main__':
	run()
