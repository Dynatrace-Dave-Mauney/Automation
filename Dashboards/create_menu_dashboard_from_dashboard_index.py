import json
import glob

GENERATED_NAME = 'Generated Dashboards'
GENERATED_ID = 'aaaaaaaa-bbbb-cccc-dddd-100000000000'

INPUT_FILE = '../DynatraceDashboardGenerator/dashboard_index.txt'
OUTPUT_FILE = f'../DynatraceDashboardGenerator/{GENERATED_ID}.json'

OLD_ID_PATTERN = 'aaaaaaaa-bbbb-cccc-dddd-0'
NEW_ID_PATTERN = 'aaaaaaaa-bbbb-cccc-dddd-1'

SORT_BY_NAME = True

dashboard_template_top = '''{
  "metadata": {
    "configurationVersions": [
      5
    ],
    "clusterVersion": "1.251.142.20220929-111511"
  },
  "id": "$$GENERATED_ID$$",
  "dashboardMetadata": {
    "name": "$$GENERATED_NAME$$",
    "shared": true,
    "sharingDetails": {
        "linkShared": true,
        "published": true
    },
    "owner": "nobody@example.com"
  },
  "tiles": [
    {
      "name": "Markdown",
      "tileType": "MARKDOWN",
      "configured": true,
      "bounds": {
        "top": 0,
        "left": 0,
        "width": 2660,
        "height": 3800
      },
      "tileFilter": {},'''

dashboard_template_bottom = '''    }
  ]
}'''

'''
Some Examples of markdown links:
"markdown": "## Menu\n\n[link](https://dynatrace.com)"
"markdown": "#[Overview](#dashboard;id=bbbbbbbb-0001-0000-0000-000000000000)\n#[Executive Overview](#dashboard;gtf=l_24_HOURS;gf=all;id=bbbbbbbb-a004-a017-0000-000000000001)\n#[SRE RUM](#dashboard;gtf=-2h;gf=all;id=bbbbbbbb-a001-a014-0000-000000000002)\n#[SRE Services](#dashboard;gtf=-1h;gf=all;id=bbbbbbbb-a001-a014-0000-000000000003)  \n"
'''

links = ''

lines = []
line_tuples = []

with open(INPUT_FILE) as input_file:
    lines = input_file.read().splitlines()

for line in lines:
    line_splits = line.split(':')
    dashboard_id = line_splits[0].replace(OLD_ID_PATTERN, NEW_ID_PATTERN)
    dashboard_name = line_splits[1]
    line_tuples.append((dashboard_id, dashboard_name))

if SORT_BY_NAME:
    line_tuples_final = sorted(line_tuples, key = lambda x: x[1])
else:
    line_tuples_final = line_tuples

for line_tuple in line_tuples_final:
    dashboard_id = line_tuple[0]
    dashboard_name = line_tuple[1]
    if dashboard_id != GENERATED_ID:
        # TODO: Support more than 10k characters. Until then, skip dashboards that are not relevant.
        if 'Azure' not in dashboard_name and \
            'Google' not in dashboard_name:
            links = links + '[' + dashboard_name + '](#dashboard;id=' + dashboard_id + ')  \\n'
            if len(links) > 10000:
                print(f'Limit Reached at {dashboard_id}:{dashboard_name}!')
                print(f'Filter out some dashboards to make the markdown tile links shorter')
                exit()

top = dashboard_template_top.replace('$$GENERATED_ID$$', GENERATED_ID).replace('$$GENERATED_NAME$$', GENERATED_NAME)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
    file.write(top)
    file.write('"markdown": "' + links + '"')
    file.write(dashboard_template_bottom)
