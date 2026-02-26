from Reuse import dynatrace_api
from Reuse import environment


def process(env_name, env, token):
	print('Environment Name:' + env_name)
	print('Environment URL: ' + env)

	endpoint = '/api/config/v1/managementZones'
	management_zones_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

	count = 0
	# delete_list = ['f0c29915-7717-4afd-9ed0-a6031fa670cd']
	delete_list = []

	for management_zones_json in management_zones_json_list:
		# print(management_zones_json)
		inner_management_zones_json_list = management_zones_json.get('values')
		for inner_management_zones_json in inner_management_zones_json_list:
			management_zone_id = inner_management_zones_json.get('id')
			name = inner_management_zones_json.get('name')

			# # # CAUTION HERE!!!! # # #
			# # # More flexible delete options are more dangerous! # # #

			# if name.startswith('HG:'):
			if '=' in name:
			# if True:
				# print(name)
				delete_list.append(management_zone_id + ': ' + name)

	delete_list = sorted(delete_list)
	delete_count = len(delete_list)

	if delete_count > 0:
		print('MANAGEMENT ZONES TO BE DELETED: ')
		for line in delete_list:
			print(line)

		msg = f'PROCEED WITH DELETE OF {delete_count} LISTED management_zones?'
		proceed = input("%s (Y/n) " % msg).upper() == 'Y'

		if proceed:
			for line in delete_list:
				management_zone_id = line.split(':', 1)[0]
				endpoint = '/api/config/v1/managementZones/' + management_zone_id
				dynatrace_api.delete_object(f'{env}{endpoint}', token)
				print('DELETED: ' + line)
				count += 1

	print('Management Zones Deleted: ' + str(count))


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
