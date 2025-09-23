from Reuse import dynatrace_api
from Reuse import environment


def process(env_name, env, token):
	print('Environment Name:' + env_name)
	print('Environment URL: ' + env)

	endpoint = '/api/config/v1/dashboards'
	dashboards_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

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
			# print(owner, dashboard_id)
			# if 'mauney' in owner.lower() or 'capes' in owner.lower():
			# if 'mauney' in owner.lower() and not name.startswith('Upper'):
			if True:
				# print(name)
				# if dashboard_id.startswith('aaaaaaaa'):
				# if name.endswith('-PROD SLOs'):
				# if 'SQL Server' in name and not dashboard_id.startswith('00000000-dddd-bbbb-ffff-0000000000'):
				# if not name.startswith('Prod:') and not name.startswith('TEMP:'):
				# if dashboard_id.startswith('aaaaaaaa-bbbb-cccc-dddd-'):
				# Mass cleanup of Overview Framework Dashboards not needed for current customer
				# if ': AWS' in name or ': Azure' in name or ': DB2' in name or ': F5' in name or ': Kafka' in name or ': IBM' in name or ': Microsoft' in name or ': Oracle' in name or ': VMware' in name or ': WebSphere' in name or ': SAP' in name or ': SOLR' in name:
				# if True:
				# if dashboard_id.startswith('00000000-dddd-bbbb-ffff-'):
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
	delete_count = len(delete_list)

	if delete_count > 0:
		print('DASHBOARDS TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = f'PROCEED WITH DELETE OF {delete_count} LISTED DASHBOARDS?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				dashboard_id = line.split(':', 1)[0]
				endpoint = '/api/config/v1/dashboards/' + dashboard_id
				dynatrace_api.delete_object(f'{env}{endpoint}', token)
				print('DELETED: ' + line)
				count += 1

	print('Dashboards Deleted: ' + str(count))


def run():
	friendly_function_name = 'Dynatrace Automation'
	env_name_supplied = environment.get_env_name(friendly_function_name)
	# For easy control from IDE
	env_name_supplied = 'Prod'
	# env_name_supplied = 'PreProd'
	# env_name_supplied = 'Sandbox'
	# env_name_supplied = 'Personal'
	env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)
	process(env_name, env, token)


if __name__ == '__main__':
	run()
