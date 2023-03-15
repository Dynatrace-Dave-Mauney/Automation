from inspect import currentframe

from Reuse import dynatrace_api
from Reuse import environment

# env_name, env, token = environment.get_environment('Prod')
# env_name, env, token = environment.get_environment('Prep')
# env_name, env, token = environment.get_environment('Dev')
env_name, env, token = environment.get_environment('Personal')
# env_name, env, token = environment.get_environment('FreeTrial1')


def get_line_number():
    cf = currentframe()
    return cf.f_back.f_lineno


def process():
    mda_dict = {}

    # Note 'mdaId' is in the list solely to check for any MDA reference beyond the targets listed below it
    mda_list = [
        'mdaId',
        'dd458841-9bbe-4d3e-bb5e-5562e3420f8b',
        '144b80d2-dbf6-46e5-97d8-2d30355cde58',
        'c1b30b11-db5c-42f8-a67f-691496788ad9',
        '48ec22c7-3350-409f-aa2e-9500c3db81c9',

    ]
    for mda in mda_list:
        mda_dict[mda] = {'dashboards': []}

    endpoint = '/api/config/v1/dashboards'
    params = ''
    dashboards_json_list = dynatrace_api.get(env, token, endpoint, params)
    dashboard_id_list = []
    for dashboards_json in dashboards_json_list:
        inner_dashboards_json_list = dashboards_json.get('dashboards')
        for inner_dashboards_json in inner_dashboards_json_list:
            entity_id = inner_dashboards_json.get('id')
            dashboard_id_list.append(entity_id)
    for dashboard_id in sorted(dashboard_id_list):
        dashboard_json = dynatrace_api.get(env, token, endpoint + '/' + dashboard_id, params)
        for dashboard in dashboard_json:
            dashboard_metadata = dashboard.get('dashboardMetadata')
            name = dashboard_metadata.get('name')
            for mda in sorted(mda_list):
                if mda in str(dashboard):
                    try:
                        print(f'MDA {mda} found in dashboard {name}')
                        dashboard_list = mda_dict[mda].get('dashboards')
                        if name not in dashboard_list:
                            dashboard_list.append(name)
                            mda_dict[mda]['dashboards'] = dashboard_list
                    except KeyError:
                        print(f'MDA {mda} found in dashboard {name} but not in target list')

    display_findings(mda_dict)


def display_findings(mda_dict):
    # print(mda_dict)
    print('Findings:')
    keys = sorted(mda_dict.keys())
    for key in keys:
        # print(key)
        mda_xref = mda_dict[key]
        # print(mda_xref)
        mda_xref_keys = mda_xref.keys()
        for mda_xref_key in mda_xref_keys:
            # print(mda_xref_key)
            if len(mda_xref[mda_xref_key]) > 0:
                print(key + ' used in ' + mda_xref_key + ': ' + sort_and_stringify_list_items(mda_xref[mda_xref_key]))


def sort_and_stringify_list_items(any_list):
    list_str = str(sorted(any_list))
    list_str = list_str.replace('[', '')
    list_str = list_str.replace(']', '')
    list_str = list_str.replace("'", "")
    list_str = list_str.replace(' ', '')
    return list_str


if __name__ == '__main__':
    process()
