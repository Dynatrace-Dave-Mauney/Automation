import xlsxwriter


def write_console(title, headers, rows, delimiter):
    console_tuple_list = [(title, headers, rows, delimiter)]
    write_console_group(console_tuple_list)


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


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')
