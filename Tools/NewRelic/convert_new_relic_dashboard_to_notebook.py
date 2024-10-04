import copy
import json
import os

from Reuse import environment

# get from configurations.yaml
include_page_list = []
include_tile_list = []
exclude_page_list = []
exclude_tile_list = []

root_directory = 'NewRelicDashboards/customer_specific'

new_relic_data = []


def process_new_relic_dashboard(filename):
    # print(f'process_new_relic_dashboard({filename})')

    global new_relic_data

    dashboard = read_json(filename)
    pages = dashboard.get('pages')
    for page in pages:
        page_name = page.get('name')
        # Process pages based on include/exclude lists
        if (not include_page_list and not exclude_page_list) or \
                (page_name in include_page_list and page_name not in exclude_page_list):
            print(f'PAGE: {page_name} pass {include_page_list} {include_page_list}')
            pass
        else:
            print(f'PAGE: {page_name} continue')
            continue

        widgets = page.get('widgets')
        for widget in widgets:
            widget_title = widget.get('title')

            # Process tiles based on include/exclude lists
            if (not include_tile_list and not exclude_tile_list) or \
                    (widget_title in include_tile_list and page_name not in exclude_tile_list):
                print(f'TILE: {widget_title} pass')
                pass
            else:
                print(f'TILE: {widget_title} continue')
                continue

            widget_visualization = widget.get('visualization')
            widget_visualization_id = widget_visualization.get('id')

            widget_raw_configuration = widget.get('rawConfiguration')
            widget_nrql_queries = widget_raw_configuration.get('nrqlQueries')

            if widget_nrql_queries:
                for widget_nrql_query in widget_nrql_queries:
                    widget_query = widget_nrql_query.get('query')
                    # print(filename, page_name, widget_title, widget_query, widget_visualization_id)
                    new_relic_data.append((filename, page_name, widget_title, widget_query, widget_visualization_id))

    if new_relic_data:
        generate_dynatrace_notebook()
        new_relic_data = []


def read_json(filename):
    # print(f'read_json({filename})')
    with open(filename, 'r', encoding='utf-8') as file:
        json_data = json.loads(file.read())
        return json_data


def process_new_relic_dashboards():
    # print('process_new_relic_dashboards()')
    configuration_file = 'configurations.yaml'
    global include_page_list
    global include_tile_list
    global root_directory
    include_page_list = environment.get_configuration('include_page_list', configuration_file=configuration_file)
    include_tile_list = environment.get_configuration('include_tile_list', configuration_file=configuration_file)
    root_directory = environment.get_configuration('root_directory', configuration_file=configuration_file)

    print(include_page_list, include_tile_list, root_directory)

    filenames = [os.path.join(path, name) for path, subdirs, files in os.walk(root_directory) for name in files]
    for filename in filenames:
        if filename.endswith('.json'):
            process_new_relic_dashboard(filename)


def get_notebook_template():
    # print('get_notebook_template()')
    notebook_template_file_name = 'dynatrace_notebook_template.json'
    with open(notebook_template_file_name, 'r', encoding='utf-8') as file:
        notebook = json.loads(file.read())
        return notebook


def generate_dynatrace_notebook():
    # print(f'generate_dynatrace_notebook()')

    print('New Relic Data:')
    for new_relic in new_relic_data:
        print(new_relic)
    print('')

    dynatrace_notebook_template = copy.deepcopy(get_notebook_template())
    notebook = copy.deepcopy(dynatrace_notebook_template)
    sections = copy.deepcopy(notebook.get('sections'))
    notebook['sections'] = []
    id_number = 1
    filename = None
    last_filename = None
    for inner_list in new_relic_data:
        for filename, page_name, widget_title, widget_query, widget_visualization_id in [inner_list]:
            dql_section = copy.deepcopy(sections[0])
            if filename != last_filename:
                if last_filename is not None:
                    write_notebook(last_filename, notebook)
                    last_filename = filename
                    id_number += 1

            comments = f'// Title: {widget_title}\n// Visualization: {widget_visualization_id}\n'
            dql_section['state']['input']['value'] = f'{comments}// NRQL: {widget_query}'
            notebook['sections'].append(dql_section)
            print(f'Appending {dql_section}')

            # name = widget_title
            # name += ': ' + str(widget_query)
    write_notebook(filename, notebook)


def write_notebook(filename, notebook):
    # print(f'write_notebook({filename}, {notebook})')
    notebook_file_name = filename.replace('NewRelic', 'Dynatrace').replace('Dashboard', 'Notebook')
    with open(notebook_file_name, 'w') as file:
        file.write(json.dumps(notebook, indent=4, sort_keys=False))
    print('wrote: ' + notebook_file_name)


def main():
    # print('main()')
    process_new_relic_dashboards()


if __name__ == '__main__':
    # print('main')
    main()
