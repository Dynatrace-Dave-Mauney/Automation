import copy
from inspect import currentframe
import os
import requests
import ssl
import time
from requests import Response

# env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
# env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
# env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
# env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

tenant = os.environ.get(tenant_key)
token = os.environ.get(token_key)
env = f'https://{tenant}.live.dynatrace.com'

offline = False
confirmation_required = True


def process():
	# For when everything is commented out below...
	pass

	print('Environment:     ' + env_name)
	print('Environment URL: ' + env)

	cleanup()

	exit(0)


def delete(endpoint, object_id):
	url = env + endpoint + '/' + object_id
	print(url)
	try:
		r: Response = requests.delete(url, headers={'Authorization': 'Api-Token ' + token, 'Content-Type': 'application/json; charset=utf-8'})
		if r.status_code == 204:
			print('Deleted ' + object_id + ' (' + endpoint + ')')
		else:
			print('Status Code: %d' % r.status_code)
			print('Reason: %s' % r.reason)
			if len(r.text) > 0:
				print(r.text)
		if r.status_code not in [200, 201, 204]:
			# print(json_data)
			print('Error in "delete(endpoint, object_id)" method')
			print('Env: ' + env)
			print('Endpoint: ' + endpoint)
			print('Token: ' + token)
			print('Object ID: ' + object_id)
			print('Exit code shown below is the source code line number of the exit statement invoked')
			exit(get_line_number())
		return r
	except ssl.SSLError:
		print('SSL Error')
		exit(get_line_number())


def get_line_number():
	cf = currentframe()
	return cf.f_back.f_lineno


def cleanup():
	endpoint = '/api/v2/settings/objects'
	for object_id in [
		# 'vu9U3hXa3q0AAAABACNidWlsdGluOmxvZ21vbml0b3JpbmcubG9nLWRwcC1ydWxlcwAGdGVuYW50AAZ0ZW5hbnQAJDhhM2I1OTQ2LTA0OWItNTkwOC04MDc3LTk5MjUzMWEyZDM3Yb7vVN4V2t6t',
		# 'vu9U3hXa3q0AAAABACNidWlsdGluOmxvZ21vbml0b3JpbmcubG9nLWRwcC1ydWxlcwAGdGVuYW50AAZ0ZW5hbnQAJDEyYmI2Y2MzLTM5YjItM2I4Ny04MTE0LWFjMjM2OTI2ZDg5Mr7vVN4V2t6t',
	]:
		delete(endpoint, object_id)


def confirm(message):
	if confirmation_required:
		proceed = input('%s (Y/n) ' % message).upper() == 'Y'
		if not proceed:
			exit()


if __name__ == '__main__':
	process()
