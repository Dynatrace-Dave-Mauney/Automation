import json

f = open('config_v1_spec3.json',)
data = json.load(f)
paths = data.get('paths')

endpoint_methods = {}
endpoints = list(paths.keys())

for endpoint in endpoints:
    endpoint_dict = paths.get(endpoint)
    methods = list(endpoint_dict.keys())
    print(endpoint + ': ' + str(methods))
    endpoint_methods[endpoint] = methods

print('Endpoint Methods:')
print(endpoint_methods)

f.close()
