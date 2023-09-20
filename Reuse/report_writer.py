import datetime
import os
import sys
import xlsxwriter

from Reuse import directories_and_files
from Reuse import environment


def write_console(title, headers, rows, delimiter):
    console_tuple_list = [(title, headers, rows, delimiter)]
    write_console_group(console_tuple_list)


def write_console_plain_text(rows):
    for row in rows:
        print(row)


def write_console_group(console_tuple_list):
    for console_tuple in console_tuple_list:
        title, headers, rows, delimiter = console_tuple

        print(title)

        max_column_index = len(headers) - 1

        column_index = 0
        output = ''
        for header in headers:
            output += header
            if column_index < max_column_index:
                output += delimiter
            column_index += 1
        print(output)

        for row in rows:
            column_index = 0
            output = ''
            for column in row:
                output += str(column)
                if column_index < max_column_index:
                    output += delimiter
                column_index += 1
            print(output)


def write_xlsx(file_name, worksheet_name, headers, rows, header_format, auto_filter):
    # Write one worksheet to an Excel workbook file
    worksheet_tuple_list = [(worksheet_name, headers, rows, header_format, auto_filter)]
    write_xlsx_worksheets(file_name, worksheet_tuple_list)


def write_xlsx_worksheets(file_name, worksheet_tuple_list):
    if not file_name:
        file_name = prepare_output_file('xlsx')

    # print(f'XLSX Output File: {file_name}')

    # Write one or more worksheets to an Excel workbook file
    workbook = xlsxwriter.Workbook(file_name)

    for worksheet_tuple in worksheet_tuple_list:
        worksheet_name, headers, rows, header_format, auto_filter = worksheet_tuple

        worksheet = workbook.add_worksheet(worksheet_name)

        if header_format:
            worksheet_header_format = workbook.add_format(header_format)
        else:
            worksheet_header_format = workbook.add_format({'bold': True, 'bg_color': '#B7C9E2'})

        row_index = 0
        column_index = 0

        for header in headers:
            worksheet.write(row_index, column_index, header, worksheet_header_format)
            column_index += 1
        row_index += 1

        for row in rows:
            column_index = 0
            for column in row:
                # Links can be passed as a dictionary like this:
                # {'link': {'url': 'https://www.dynatrace.com', 'text': 'Dynatrace'}}
                if isinstance(column, dict):
                    link = column.get('link', {})
                    url = link.get('url')
                    text = link.get('text')
                    if url and text:
                        worksheet.write_url(row_index, column_index, url, string=text)
                    else:
                        worksheet.write(row_index, column_index, str(column))
                else:
                    worksheet.write(row_index, column_index, column)
                column_index += 1
            row_index += 1

        if auto_filter:
            worksheet.autofilter(0, auto_filter[0], row_index, auto_filter[1])

        worksheet.autofit()

    workbook.close()


def write_html(file_name, page_heading, table_headers, rows):
    # Write one html report to file
    html_tuple_list = [(page_heading, table_headers, rows)]
    write_html_group(file_name, html_tuple_list)


def write_html_group(file_name, html_tuple_list):
    if not file_name:
        file_name = prepare_output_file('html')

    # print(f'HTML Output File: {file_name}')

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

    table_end = '       </table>'

    html_bottom = '''
    </body>
</html>'''

    row_start = '            <tr>\n'
    row_end = '            </tr>'
    col_start = '                <td>'
    col_end = '</td>\n'

    with open(file_name, 'w', encoding='utf8') as file:
        # Begin HTML formatting
        write_line(file, html_top)

        for html_tuple in html_tuple_list:
            page_heading, table_headers, rows = html_tuple

            # Write Page/Group Header
            write_h1_heading(file, page_heading)

            # Initialize Table Headers
            table_header_html = '        <table>\n'
            table_header_html += '            <tr>\n'

            for table_header in table_headers:
                table_header_html += f'                <th>{table_header}</th>\n'
            table_header_html += '            </tr>'

            # Write Table Header
            write_line(file, table_header_html)

            # Write Table Rows
            for row in rows:
                output = row_start
                for column in row:
                    output += col_start
                    output += str(column)
                    output += col_end
                output += row_end
                write_line(file, output)

            write_line(file, table_end)

        # Finish the HTML formatting
        write_line(file, html_bottom)


def write_h1_heading(outfile, heading):
    outfile.write('        <h1>' + heading + '</h1>')
    outfile.write('\n')


def initialize_text_file(file_name):
    if not file_name:
        file_name = prepare_output_file('txt')

    # print(f'Text Output File Initialized: {file_name}')
    with open(file_name, 'w', encoding='utf8') as file:
        file.write('')


def write_text(file_name, title, headers, rows, delimiter):
    text_tuple_list = [(title, headers, rows, delimiter)]
    write_text_group(file_name, text_tuple_list)


def write_plain_text(file_name, rows):
    if not file_name:
        file_name = prepare_output_file('txt')

    # print(f'Text Output File Appended (Strings): {file_name}')
    with open(file_name, 'a', encoding='utf8') as file:
        for row in rows:
            write_line(file, row)


def write_text_group(file_name, text_tuple_list):
    if not file_name:
        file_name = prepare_output_file('txt')

    # print(f'Text Output File Appended (Tuples): {file_name}')
    with open(file_name, 'a', encoding='utf8') as file:
        for text_tuple in text_tuple_list:
            title, headers, rows, delimiter = text_tuple

            write_line(file, title)

            max_column_index = len(headers) - 1

            column_index = 0
            output = ''
            for header in headers:
                output += header
                if column_index < max_column_index:
                    output += delimiter
                column_index += 1
            write_line(file, output)

            for row in rows:
                column_index = 0
                output = ''
                for column in row:
                    output += str(column)
                    if column_index < max_column_index:
                        output += delimiter
                    column_index += 1
                write_line(file, output)


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')


def prepare_output_file(file_extension):
    # Create output directory, if needed
    # Return a generated output file name based on the Python module name, using the file extension specified
    default_output_directory = '.'
    output_directory = environment.get_output_directory_name(default_output_directory)
    current_working_directory = os.getcwd()
    # print(f'Current working directory: {current_working_directory}')
    if not os.path.isdir(output_directory):
        directories_and_files.make_directory(output_directory)
        # print(f'Output directory created: {output_directory}')
    # else:
    #     print(f'Output directory already exists: {output_directory}')

    calling_module = sys.argv[0]
    # print(type(calling_module))
    # print(calling_module)
    base_module_name = calling_module.replace(current_working_directory, '').replace('\\', '').replace('/', '')
    base_file_name = base_module_name.replace('.py', f'.{file_extension}')
    # full_file_name = f'{output_directory}/{base_file_name}'
    full_file_name = os.path.join(output_directory, base_file_name)
    # print(f'full_file_name: {full_file_name}')

    return full_file_name


def stringify_list(any_list):
    any_list_string = str(any_list)
    any_list_string = any_list_string.replace('[', '')
    any_list_string = any_list_string.replace(']', '')
    any_list_string = any_list_string.replace("'", "")
    return any_list_string


def convert_epoch_in_milliseconds_to_local(epoch):
    if epoch is None or epoch == -1 or epoch == 0:
        return ''
    else:
        return datetime.datetime.fromtimestamp(epoch / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
