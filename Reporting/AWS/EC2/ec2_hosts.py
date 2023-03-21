import json
import urllib.parse

from Reuse import dynatrace_api
from Reuse import environment

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')


def dump_json(endpoint, object_id):
	r = dynatrace_api.get_by_object_id(env, token, endpoint, object_id)
	json_data = json.dumps(json.loads(r.text), indent=4, sort_keys=False)
	print(json_data)
	with open('$DUMP-' + object_id, 'w') as file:
		file.write(json_data)


def process():
	# For when everything is commented out below...
	pass

	formatted_line_list = []
	raw_endpoint = '/api/v2/entities?pageSize=4000&entitySelector=type(EC2_INSTANCE)&fields=fromRelationships.isAccessibleBy'
	endpoint = urllib.parse.quote(raw_endpoint, safe='/,&=?')
	r = dynatrace_api.get_object_list(env, token, endpoint)
	ec2_instance_json = json.loads(r.text)
	ec2_instance_list = ec2_instance_json.get('entities')
	for ec2_instance in ec2_instance_list:
		# print(ec2_instance)
		display_name = ec2_instance.get('displayName')
		if not display_name.startswith('UNKNOWN'):
			formatted_line_list.append(display_name)

	for display_name in sorted(formatted_line_list):
		print(display_name)


if __name__ == '__main__':
	process()
