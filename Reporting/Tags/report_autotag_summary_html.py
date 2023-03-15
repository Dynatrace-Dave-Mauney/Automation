import urllib.parse
from datetime import date
from itertools import groupby

from Reuse import dynatrace_api
from Reuse import environment


supported_environments = {
    'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
}

html_path = '../../$Output/Reporting'

html_top = '''<html>
  <body>
    <head>
      <style>
        table, th, td {
          border: 1px solid black;
          border-collapse: collapse;
        }
        th, td {
          padding: 5px;
        }
        th {
          text-align: left;
        }
      </style>
    </head>'''

table_header = '''    <table>
      <tr>
        <th>Tag Name</th>
        <th>Tag Description</th>
        <th>Tenants</th>
      </tr>'''

html_bottom = '''    </table>
  </body>
</html>'''


def get_tag_data(env, token):
    endpoint = '/api/config/v1/autoTags'
    raw_params = 'fields=+description'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    autotags_json_list = dynatrace_api.get(env, token, endpoint, params)

    tag_data_list = []

    for autotags_json in autotags_json_list:
        inner_autotags_json_list = autotags_json.get('values')
        for inner_autotags_json in inner_autotags_json_list:
            name = inner_autotags_json.get('name')
            description = inner_autotags_json.get('description', '')
            tag_data_list.append((name, description))

    return tag_data_list


def process(env_name_list, all_env_name_data):
    row_start = '<tr>'
    row_end = '</tr>'
    col_start = '<td>'
    col_start_bad = '<td style="color:red">'
    col_end = '</td>'

    html_line_list = []

    for key in sorted(all_env_name_data.keys()):
        autotag_data = all_env_name_data.get(key)
        autotag_name = key
        autotag_env_name_list = autotag_data.get('env_name_list')
        autotag_description_list = autotag_data.get('description_list')
        if all_equal(autotag_description_list):
            autotag_description = autotag_description_list[0]
        else:
            autotag_description = str(autotag_description_list)
        if autotag_env_name_list != env_name_list or not all_equal(autotag_description_list):
            html = f'      {row_start}{col_start_bad}{autotag_name}{col_end}{col_start}{str(autotag_description)}{col_end}{col_start}{str(autotag_env_name_list)}{col_end}{row_end}'
        else:
            html = f'      {row_start}{col_start}{autotag_name}{col_end}{col_start}{str(autotag_description)}{col_end}{col_start}{str(autotag_env_name_list)}{col_end}{row_end}'
        html_line_list.append(html)

    file_name = f'{html_path}/TagSummary.html'
    write_html(file_name, sorted(html_line_list))

    print(f'Output written to {file_name}')

def write_html(filename, html_line_list):
    with open(filename, 'w', encoding='utf8') as file:
        today = date.today()
        run_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

        # Begin HTML formatting
        write_line(file, html_top)

        # Write the tag summary header
        write_h1_heading(file, f'Dynatrace Tag Summary As Of ' + run_date)

        # Write Table Header
        write_line(file, table_header)

        # Write Table Rows
        for html_line in html_line_list:
            write_line(file, html_line)

        # Finish the HTML formatting
        write_line(file, html_bottom)


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')


def write_h1_heading(outfile, heading):
    outfile.write('    <h1>' + heading + '</h1>')
    outfile.write('\n')


def add_or_update(env_name, env_name_data, all_env_name_data):
    env_name_data_current = all_env_name_data.get(env_name_data[0])
    if env_name_data_current:
        env_name_list = env_name_data_current.get('env_name_list')
        description_list = env_name_data_current.get('description_list')
        env_name_list.append(env_name)
        description_list.append(env_name_data[1])
        all_env_name_data[env_name_data[0]] = {'env_name_list': env_name_list, 'description_list': description_list}
    else:
        all_env_name_data[env_name_data[0]] = {'env_name_list': [env_name], 'description_list': [env_name_data[1]]}


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def main():
    env_name_list = ['Prod', 'Prep', 'Dev']

    all_env_name_data = {}

    for env_name in env_name_list:
        env_name, env, token = environment.get_environment(env_name)
        env_name_data_list = get_tag_data(env, token)
        for env_name_data in env_name_data_list:
            add_or_update(env_name, env_name_data, all_env_name_data)

    # for key in sorted(all_env_name_data.keys()):
    #     print(key, str(all_env_name_data.get(key)))

    process(env_name_list, all_env_name_data)


if __name__ == '__main__':
    main()
