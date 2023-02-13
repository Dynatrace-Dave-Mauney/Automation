# Module used to analyze the config_v1_spec3.json file to help with coding the backup module

import json

def analyze_return_types():
    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    # TODO: REMOVE
    # for path in sorted(paths):
    #     print(path)
    # exit(1234)

    endpoint_methods = {}

    list_definitely = []
    list_probably = []
    list_maybe = []
    list_probably_not = []
    list_definitely_not = []

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        endpoint_dict = paths.get(endpoint)
        # print(endpoint_dict)
        methods = list(endpoint_dict.keys())
        # print(methods)
        endpoint_methods[endpoint] = methods
        if 'get' in methods:
            # get_dict = endpoint_dict.get('get')
            get_summary = endpoint_dict.get('get').get('summary', '')
            get_response = endpoint_dict.get('get').get('responses').get('200').get('content')
            if get_response:
                try:
                    get_response_ref = get_response.get('application/json; charset=utf-8').get('schema').get('$ref', 'None')
                    if get_summary.startswith('Lists') and 'List' in get_response_ref:
                        list_definitely.append(endpoint)
                    else:
                        if endpoint.endswith('{id}') and endpoint.replace('/{id}', '') in list_definitely:
                            list_definitely_not.append(endpoint)
                        else:
                            if endpoint.endswith('s'):
                                list_probably.append(endpoint)
                            else:
                                if 'list' in get_summary or 'List' in get_summary or 'List' in get_response_ref:
                                    list_maybe.append(endpoint)
                                else:
                                    list_probably_not.append(endpoint)
                    # print(f'{endpoint} {get_response_ref} {get_summary} {is_list_string}')
                    pass
                except AttributeError:
                    # print(f'{endpoint} get response should be investigated further (no $ref)')
                    pass
            else:
                print(f'{endpoint} get response should be investigated further')

    print('Definitely Returns List')
    for endpoint in list_definitely:
        print(endpoint)

    print('')
    print('=================================')
    print('')

    print('Probably Returns List')
    for endpoint in list_probably:
        print(endpoint)

    print('')
    print('=================================')
    print('')

    print('Maybe Returns List')
    for endpoint in list_maybe:
        print(endpoint)

    print('')
    print('=================================')
    print('')

    print("Probably Doesn't Return List")
    for endpoint in list_probably_not:
        print(endpoint)

    print('')
    print('=================================')
    print('')

    print("Definitely Doesn't Return List")
    for endpoint in list_definitely_not:
        print(endpoint)


def analyze_depth():
    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    endpoint_methods = {}

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        endpoint_dict = paths.get(endpoint)
        if endpoint.count('{') > 1:
            if not endpoint.endswith('/validator') and not endpoint.startswith('/symfiles'):
                print(endpoint)


def startswith(startswith_string):
    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    endpoint_methods = {}

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        if endpoint.startswith(startswith_string):
            print(endpoint)


def contains(contains_string):
    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    endpoint_methods = {}

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        if contains_string in endpoint:
            print(endpoint)


def most_complex():
    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    endpoint_methods = {}

    endpoints = sorted(list(paths.keys()))

    for endpoint in endpoints:
        if not endpoint.endswith('/validator') and not endpoint.startswith('/symfiles'):
            if '{' in endpoint and not endpoint.endswith('{id}'):
                print(endpoint)


def least_complex():
    f = open('config_v1_spec3.json', )
    data = json.load(f)
    paths = data.get('paths')

    endpoint_methods = {}

    endpoints = sorted(list(paths.keys()))

    least_complex_list = []

    for endpoint in endpoints:
        if not endpoint.endswith('/validator') and not endpoint.startswith('/symfiles'):
            if '{' not in endpoint:
                print(endpoint)
                least_complex_list.append(endpoint)

    print(least_complex_list)

if __name__ == '__main__':
    # analyze_return_types()
    # analyze_depth()
    # startswith('/extensions')
    # contains('{')
    most_complex()
    # least_complex()