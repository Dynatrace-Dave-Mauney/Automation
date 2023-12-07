from Reuse import dynatrace_api
from Reuse import environment

friendly_function_name = 'Dynatrace Automation Tools'
env_name_supplied = environment.get_env_name(friendly_function_name)
# For easy control from IDE
# env_name_supplied = 'Prod'
# env_name_supplied = 'NonProd'
# env_name_supplied = 'Prep'
# env_name_supplied = 'Dev'
env_name_supplied = 'Personal'
# env_name_supplied = 'Demo'
env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

offline = False
confirmation_required = True


def process():
	# For when everything is commented out below...
	pass

	print('Environment:     ' + env_name)
	print('Environment URL: ' + env)

	cleanup()

	exit(0)


def cleanup():
	endpoint = '/api/v2/settings/objects'
	for object_id in [
		# 'vu9U3hXa3q0AAAABACNidWlsdGluOmxvZ21vbml0b3JpbmcubG9nLWRwcC1ydWxlcwAGdGVuYW50AAZ0ZW5hbnQAJDhhM2I1OTQ2LTA0OWItNTkwOC04MDc3LTk5MjUzMWEyZDM3Yb7vVN4V2t6t',
		# 'vu9U3hXa3q0AAAABACNidWlsdGluOmxvZ21vbml0b3JpbmcubG9nLWRwcC1ydWxlcwAGdGVuYW50AAZ0ZW5hbnQAJDEyYmI2Y2MzLTM5YjItM2I4Ny04MTE0LWFjMjM2OTI2ZDg5Mr7vVN4V2t6t',
	]:
		dynatrace_api.delete_object(f'{env}{endpoint}/{object_id}', token)


def confirm(message):
	if confirmation_required:
		proceed = input('%s (Y/n) ' % message).upper() == 'Y'
		if not proceed:
			exit()


if __name__ == '__main__':
	process()
