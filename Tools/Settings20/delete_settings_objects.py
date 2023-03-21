from Reuse import dynatrace_api
from Reuse import environment

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')

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
		dynatrace_api.delete(env, token, endpoint, object_id)


def confirm(message):
	if confirmation_required:
		proceed = input('%s (Y/n) ' % message).upper() == 'Y'
		if not proceed:
			exit()


if __name__ == '__main__':
	process()
