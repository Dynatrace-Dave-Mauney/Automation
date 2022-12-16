import json


def print_header():
    info = data.get('info')
    title = info.get('title')
    description = info.get('description')
    version = info.get('version')
    # header = title + ': ' + description + ' Version: ' + version
    print(title)
    print('')
    print(description)
    print('')
    print('Version: ' + version)
    print('')


def dump_tags():
    tags = data.get('tags')
    formatted_tag_list = []
    for tag in tags:
        name = tag.get('name')
        description = tag.get('description')
        formatted_tag = name + ': ' + description
        formatted_tag_list.append(formatted_tag)

    for formatted_tag in sorted(formatted_tag_list):
        print(formatted_tag)


def dump_schemas():
    schema_keys = data.get('components').get('schemas').keys()
    formatted_schema_list = []
    for schema_key in schema_keys:
        schema = data.get('components').get('schemas').get(schema_key)
        description = schema.get('description', 'N/A')
        # schema_properties = schema.get('properties')
        read_only = schema.get('readOnly', False)
        if read_only:
            read_only_str = ' (Read Only)'
        else:
            read_only_str = ''
        formatted_schema = schema_key + ': ' + description + read_only_str
        formatted_schema_list.append(formatted_schema)

    for formatted_schema in sorted(formatted_schema_list):
        print(formatted_schema)


def dump_endpoint_methods():
    # The endpoint methods
    print('Endpoint Methods:')
    paths = data.get('paths')
    endpoint_methods = {}
    endpoints = list(paths.keys())

    for endpoint in endpoints:
        endpoint_dict = paths.get(endpoint)
        methods = list(endpoint_dict.keys())
        print(endpoint + ': ' + str(methods))
        endpoint_methods[endpoint] = methods


# Main Processing...
f = open('env_v1_spec3.json',)
data = json.load(f)
print_header()

# dump_endpoint_methods()
# dump_api_token_scopes()
# dump_tags()
dump_schemas()
