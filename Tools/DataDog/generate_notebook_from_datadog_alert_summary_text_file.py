import copy
import json
import os

# from Reuse import environment

# get from configurations.yaml
input_directory = 'customer_specific/monitors'
output_directory = 'customer_specific/dynatrace/notebooks'

datadog_data = []


def process_datadog_alert_summary_text_file(filename):
    print(f'process_datadog_alert_summary_text_file({filename})')

    global datadog_data

    lines = read_text(filename)

    index = 0
    for line in lines:
        data = line.strip()

        if data.startswith('https'):
            comment1 = f'// {lines[index - 2].strip()}'
            comment2 = f'// {lines[index - 1].strip()}'
            comment3 = f'// {lines[index].strip()}'
            datadog_data.append((filename, comment1, comment2, comment3))

        index += 1

    if datadog_data:
        generate_dynatrace_notebook()
        datadog_data = []


def read_text(filename):
    # print(f'read_text({filename})')
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return lines


def process_datadog_alert_summary_text_files():
    # configuration_file = 'configurations.yaml'
    # global input_directory
    # global output_directory
    # input_directory = environment.get_configuration('input_directory', configuration_file=configuration_file)
    # output_directory = environment.get_configuration('output_directory', configuration_file=configuration_file)

    print(input_directory, output_directory)

    filenames = [os.path.join(path, name) for path, subdirs, files in os.walk(input_directory) for name in files]
    for filename in filenames:
        if filename.endswith('Services.txt'):
            process_datadog_alert_summary_text_file(filename)


def get_notebook_template():
    # print('get_notebook_template()')
    notebook_template_file_name = 'dynatrace_notebook_template.json'
    with open(notebook_template_file_name, 'r', encoding='utf-8') as file:
        notebook = json.loads(file.read())
        return notebook


def generate_dynatrace_notebook():
    # print(f'generate_dynatrace_notebook()')

    print('DataDog Data:')
    for datadog in datadog_data:
        print(datadog)
    print('')

    dynatrace_notebook_template = copy.deepcopy(get_notebook_template())
    notebook = copy.deepcopy(dynatrace_notebook_template)
    sections = copy.deepcopy(notebook.get('sections'))
    notebook['sections'] = []
    id_number = 1
    filename = None
    last_filename = None
    for inner_list in datadog_data:
        for filename, comment1, comment2, comment3 in [inner_list]:
            dql_section = copy.deepcopy(sections[0])
            if filename != last_filename:
                if last_filename is not None:
                    write_notebook(last_filename, notebook)
                    last_filename = filename
                    id_number += 1

            comments = f'{comment1}\n{comment2}\n{comment3}\n'
            dql_section['state']['input']['value'] = comments

            notebook['sections'].append(dql_section)
            print(f'Appending {dql_section}')

    write_notebook(filename, notebook)


def write_notebook(filename, notebook):
    # print(f'write_notebook({filename}, {notebook})')
    global input_directory
    global output_directory
    notebook_file_name = filename.replace(input_directory, output_directory).replace('.txt', '.json')
    with open(notebook_file_name, 'w') as file:
        file.write(json.dumps(notebook, indent=4, sort_keys=False))
    print('wrote: ' + notebook_file_name)


def main():
    process_datadog_alert_summary_text_files()


if __name__ == '__main__':
    main()
