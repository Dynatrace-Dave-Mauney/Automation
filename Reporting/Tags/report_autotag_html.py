import dynatrace_rest_api_helper
import os
import urllib.parse
from datetime import date

env_name = ''

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
      </tr>'''

html_bottom = '''    </table>
  </body>
</html>'''


def process(env, token):
    endpoint = '/api/config/v1/autoTags'
    raw_params = 'fields=+description'
    params = urllib.parse.quote(raw_params, safe='/,&=')
    autotags_json_list = dynatrace_rest_api_helper.get_rest_api_json(env, token, endpoint, params)

    row_start = '<tr>'
    row_end = '</tr>'
    col_start = '<td>'
    col_end = '</td>'

    html_line_list = []

    for autotags_json in autotags_json_list:
        inner_autotags_json_list = autotags_json.get('values')
        for inner_autotags_json in inner_autotags_json_list:
            # entity_id = inner_autotags_json.get('id')
            name = inner_autotags_json.get('name')
            description = inner_autotags_json.get('description', '')

            html = f'      {row_start}{col_start}{name}{col_end}{col_start}{description}{col_end}{row_end}'
            html_line_list.append(html)

            write_html(f'{html_path}/TagSummary_For_{env_name}.html', sorted(html_line_list))


def write_html(filename, html_line_list):
    with open(filename, 'w', encoding='utf8') as file:
        today = date.today()
        run_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

        # Begin HTML formatting
        write_line(file, html_top)

        # Write the tag summary header
        write_h1_heading(file, f'Dynatrace Tag Summary for {env_name} As Of ' + run_date)

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


def main():
    global env_name
    # env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
    # env_name, tenant_key, token_key = ('Prep', 'PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN')
    env_name, tenant_key, token_key = ('Dev', 'DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN')
    # env_name, tenant_key, token_key = ('Personal', 'PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN')

    tenant = os.environ.get(tenant_key)
    token = os.environ.get(token_key)
    env = f'https://{tenant}.live.dynatrace.com'

    masked_token = token.split('.')[0] + '.' + token.split('.')[1] + '.* (Masked)'

    print(f'Environment Name: {env_name}')
    print(f'Environment:      {env}')
    print(f'Token:            {masked_token}')

    print('')
    print('Report Autotag HTML')

    process(env, token)


if __name__ == '__main__':
    main()
