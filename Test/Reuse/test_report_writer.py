from Reuse import report_writer


def test_write_console():
    title = 'Test'
    headers = ('Column1Header', 'Column2Header', 'Column3Header', 'Column4Header')
    delimiter = '|'
    rows = []
    rows.append(('Row1Column1', 'Row1Column2', 'Row1Column3', 1))
    rows.append(('Row2Column1', 'Row2Column2', 'Row2Column3', 2))
    rows.append(('Row3Column1', 'Row3Column2', 'Row3Column3', 3))
    rows.append(('Row4Column1', 'Row4Column2', 'Row4Column3', 4))
    rows.append(('Row5Column1', 'Row5Column2', 'Row5Column3', 5))
    report_writer.write_console(title, headers, rows, delimiter)

def test_write_xlsx():
    file_name = 'test_report.xlsx'
    worksheet_name = 'Test'
    # header_format = {'bold': True, 'bg_color': '#B7C9E2'}
    header_format = None
    auto_filter = (2, 2)
    # auto_filter = None
    headers = ('Column1Header', 'Column2Header', 'Column3Header', 'Column4Header')

    dynatrace_link = {'link': {'url': 'https://www.dynatrace.com', 'text': 'Dynatrace'}}

    rows = []
    rows.append(('Row1Column1', 'Row1Column2', dynatrace_link, 1))
    rows.append(('Row2Column1', 'Row2Column2', dynatrace_link, 2))
    rows.append(('Row3Column1', 'Row3Column2', dynatrace_link, 3))
    rows.append(('Row4Column1', 'Row4Column2', dynatrace_link, 4))
    rows.append(('Row5Column1', 'Row5Column2', dynatrace_link, 5))

    report_writer.write_xlsx(file_name, worksheet_name, headers, rows, header_format, auto_filter)


def test_write_html():
    file_name = 'test_report.html'
    page_heading = 'Test'
    table_headers = ('Column1Header', 'Column2Header', 'Column3Header', 'Column4Header')

    dynatrace_link = f'<a href="https://www.dynatrace.com">Dynatrace</a>'

    rows = []
    rows.append(('Row1Column1', 'Row1Column2', dynatrace_link, 1))
    rows.append(('Row2Column1', 'Row2Column2', dynatrace_link, 2))
    rows.append(('Row3Column1', 'Row3Column2', dynatrace_link, 3))
    rows.append(('Row4Column1', 'Row4Column2', dynatrace_link, 4))
    rows.append(('Row5Column1', 'Row5Column2', dynatrace_link, 5))

    report_writer.write_html(file_name, page_heading, table_headers, rows)


def main():
    test_write_console()
    test_write_xlsx()
    test_write_html()

if __name__ == '__main__':
    main()
