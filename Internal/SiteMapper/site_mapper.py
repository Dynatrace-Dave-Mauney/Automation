import requests
import yaml
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import date

html_top = '''<html>
<body>
<table>
  <tr>
    <th>Title</th>
    <th>Author</th>
    <th>Publish Date</th>
  </tr>
'''

html_bottom = '''</table>
</body>
</html>'''

site_map_url_list = [
    'https://www.dynatrace.com/news/post-sitemap.xml',
    'https://www.dynatrace.com/news/post-sitemap2.xml'
]


def read_yaml(filename):
    try:
        with open(filename, 'r') as file:
            document = file.read()
            return yaml.load(document, Loader=yaml.FullLoader)
    except FileNotFoundError:
        return []


def write_yaml(filename, any_list):
    with open(filename, 'w') as file:
        yaml.dump(any_list, file, sort_keys=False)


def write_html(filename, html_line_list):
    with open(filename, 'w', encoding='utf8') as file:
        today = date.today()
        run_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

        # Begin HTML formatting
        write_line(file, html_top)

        # Write the environment summary header
        write_h1_heading(file, 'Dynatrace News History As Of ' + run_date)

        for html_line in html_line_list:
            write_line(file, html_line)

        # Finish the HTML formatting
        write_line(file, html_bottom)


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')


def write_h1_heading(outfile, heading):
    outfile.write('<h1>' + heading + '</h1>')
    outfile.write('\n')


def format_html(page_data_list):
    html_list = []
    for page_data in page_data_list:
        row_start = '<tr>'
        row_end = '</tr>'
        col_start = '<td>'
        col_end = '</td>'
        url = page_data[0]
        title = page_data[1]
        author = page_data[2]
        pub_date = page_data[3].split('T')[0]
        html = f'{row_start}{col_start}<a href="{url}">{title}</a>{col_end}{col_start}{author}{col_end}{col_start}{pub_date}{col_end}{row_end}'
        html_list.append(html)
    return html_list


def get_page_url_list():
    page_url_list = []

    for site_map_url in site_map_url_list:
        site_map = requests.get(site_map_url)
        site_root = ET.fromstring(site_map.text)
        for child in site_root:
            if child.tag.endswith('url'):
                for url_child in child:
                    if url_child.tag.endswith('loc'):
                        url = url_child.text
                        if url != "https://www.dynatrace.com/news/blog/" and "release-notes-version" not in url and "feature-update-version" not in url:
                            page_url_list.append(url_child.text)

    return page_url_list


def get_page_data_list(page_url_list):
    page_data_list = []

    # DEBUG: Use to test small number of urls
    # count = 0
    for page_url in page_url_list:
        # count += 1
        # if count > 10:
        #     break
        page = requests.get(page_url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        title = page_soup.find("meta", property="og:title")
        author = page_soup.find('meta', attrs={'name': 'author'})
        pub_date = page_soup.find("meta", property="article:published_time")
        if title and author and pub_date:
            page_data_list.append((page_url, title.get('content'), author.get('content'), pub_date.get('content')))

    return page_data_list


def process():
    known_pages = read_yaml('known_pages.yaml')
    known_urls = []
    for known_page in known_pages:
        known_urls.append(known_page[0])

    page_url_list = get_page_url_list()

    unknown_urls = []
    for page_url in page_url_list:
        if page_url not in known_urls:
            unknown_urls.append(page_url)
            print(f'Unknown URL {page_url}')

    page_data_list = get_page_data_list(unknown_urls)
    page_data_list.extend(known_pages)

    # One time removal of duplicates
    page_data_list = [*set(page_data_list)]

    page_data_list.sort(key=lambda y: y[3], reverse=True)

    write_yaml('known_pages.yaml', page_data_list)
    write_html('dynatrace_news_history.html', format_html(page_data_list))


if __name__ == '__main__':
    process()
