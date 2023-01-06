import requests
import yaml
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import date

html_path = '../../docs'

html_top_blogs = '''<html>
<body>
<table>
  <tr>
    <th>Title</th>
    <th>Author</th>
    <th>Publish Date</th>
  </tr>
'''

html_top_release_notes = '''<html>
<body>
<table>
  <tr>
    <th>Title</th>
  </tr>
'''

html_bottom = '''</table>
</body>
</html>'''

site_map_url_list = [
    'https://www.dynatrace.com/news/post-sitemap.xml',
    'https://www.dynatrace.com/news/post-sitemap2.xml'
]


def get_url_lists():
    blog_url_list = []
    saas_release_notes_url_list = []
    managed_release_notes_url_list = []
    one_agent_release_notes_url_list = []
    active_gate_release_notes_url_list = []

    for site_map_url in site_map_url_list:
        site_map = requests.get(site_map_url)
        site_root = ET.fromstring(site_map.text)
        for child in site_root:
            if child.tag.endswith('url'):
                for url_child in child:
                    if url_child.tag.endswith('loc'):
                        url = url_child.text
                        if url != "https://www.dynatrace.com/news/blog/":
                            if "release-notes-version" not in url and "feature-update-version" not in url:
                                blog_url_list.append(url_child.text)
                            else:
                                if "managed" in url:
                                    managed_release_notes_url_list.append(url_child.text)
                                else:
                                    if "saas" in url:
                                        saas_release_notes_url_list.append(url_child.text)
                                    else:
                                        if "oneagent-release-notes" in url:
                                            one_agent_release_notes_url_list.append(url_child.text)
                                        else:
                                            if "security-gateway-release-notes" in url or "activegate-release-notes" in url:
                                                active_gate_release_notes_url_list.append(url_child.text)

    return blog_url_list, saas_release_notes_url_list, managed_release_notes_url_list, one_agent_release_notes_url_list, active_gate_release_notes_url_list


def get_blog_page_data_list(blog_url_list):
    blog_page_data_list = []

    # DEBUG: Use to test small number of urls
    # count = 0
    for blog_url in blog_url_list:
        # count += 1
        # if count > 10:
        #     break
        page = requests.get(blog_url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        title = page_soup.find("meta", property="og:title")
        author = page_soup.find('meta', attrs={'name': 'author'})
        pub_date = page_soup.find("meta", property="article:published_time")
        if title and author and pub_date:
            blog_page_data_list.append((blog_url, title.get('content'), author.get('content'), pub_date.get('content')))

    return blog_page_data_list


def get_release_notes_page_data_list(release_notes_url_list):
    release_notes_page_data_list = []

    # DEBUG: Use to test small number of urls
    # count = 0
    for release_notes_url in release_notes_url_list:
        # count += 1
        # if count > 10:
        #     break
        page = requests.get(release_notes_url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        title = page_soup.find("meta", property="og:title")
        author = 'Dynatrace'
        pub_date = page_soup.find("meta", property="article:published_time")
        if title and author and pub_date:
            release_notes_page_data_list.append((release_notes_url, title.get('content'), author, pub_date.get('content')))

    return release_notes_page_data_list


def write_html(page_type, filename, html_line_list):
    with open(filename, 'w', encoding='utf8') as file:
        today = date.today()
        run_date = str(today.month) + '/' + str(today.day) + '/' + str(today.year)

        # Begin HTML formatting
        if page_type == 'News':
            write_line(file, html_top_blogs)
        else:
            write_line(file, html_top_release_notes)

        # Write the environment summary header
        write_h1_heading(file, f'Dynatrace {page_type} History As Of ' + run_date)

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


def format_html(page_type, blog_page_data_list):
    html_list = []
    for blog_page_data in blog_page_data_list:
        row_start = '<tr>'
        row_end = '</tr>'
        col_start = '<td>'
        col_end = '</td>'
        url = blog_page_data[0]
        title = blog_page_data[1]
        author = blog_page_data[2]
        pub_date = blog_page_data[3].split('T')[0]
        if page_type == 'News':
            html = f'{row_start}{col_start}<a href="{url}">{title}</a>{col_end}{col_start}{author}{col_end}{col_start}{pub_date}{col_end}{row_end}'
        else:
            html = f'{row_start}{col_start}<a href="{url}">{title}</a>{col_end}{row_end}'
        html_list.append(html)
    return html_list


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


def process_blogs(blog_url_list):
    known_blog_pages = read_yaml('known_blog_pages.yaml')
    known_blog_urls = []
    for known_blog_page in known_blog_pages:
        known_blog_urls.append(known_blog_page[0])

    unknown_blog_urls = []
    for blog_url in blog_url_list:
        if blog_url not in known_blog_urls:
            unknown_blog_urls.append(blog_url)
            print(f'Unknown URL {blog_url}')

    blog_page_data_list = get_blog_page_data_list(unknown_blog_urls)
    blog_page_data_list.extend(known_blog_pages)

    # One time removal of duplicates
    # blog_page_data_list = [*set(blog_page_data_list)]

    blog_page_data_list.sort(key=lambda y: y[3], reverse=True)

    write_yaml('known_blog_pages.yaml', blog_page_data_list)
    write_html('News', f'{html_path}/dynatrace_news_history.html', format_html('News', blog_page_data_list))


def process_saas_release_notes(saas_release_notes_url_list):
    known_saas_release_notes_pages = read_yaml('known_saas_release_notes_pages.yaml')
    known_saas_release_notes_urls = []
    for known_saas_release_notes_page in known_saas_release_notes_pages:
        known_saas_release_notes_urls.append(known_saas_release_notes_page[0])

    unknown_saas_release_notes_urls = []
    for saas_release_notes_url in saas_release_notes_url_list:
        if saas_release_notes_url not in known_saas_release_notes_urls:
            unknown_saas_release_notes_urls.append(saas_release_notes_url)
            print(f'Unknown URL {saas_release_notes_url}')

    saas_release_notes_page_data_list = get_release_notes_page_data_list(unknown_saas_release_notes_urls)
    saas_release_notes_page_data_list.extend(known_saas_release_notes_pages)

    # One time removal of duplicates
    # saas_release_notes_page_data_list = [*set(saas_release_notes_page_data_list)]

    saas_release_notes_page_data_list.sort(key=lambda y: y[1], reverse=True)

    write_yaml('known_saas_release_notes_pages.yaml', saas_release_notes_page_data_list)
    write_html('SaaS Release Notes', f'{html_path}/dynatrace_saas_release_notes_history.html', format_html('Release Notes', saas_release_notes_page_data_list))


def process_managed_release_notes(managed_release_notes_url_list):
    known_managed_release_notes_pages = read_yaml('known_managed_release_notes_pages.yaml')
    known_managed_release_notes_urls = []
    for known_managed_release_notes_page in known_managed_release_notes_pages:
        known_managed_release_notes_urls.append(known_managed_release_notes_page[0])

    unknown_managed_release_notes_urls = []
    for managed_release_notes_url in managed_release_notes_url_list:
        if managed_release_notes_url not in known_managed_release_notes_urls:
            unknown_managed_release_notes_urls.append(managed_release_notes_url)
            print(f'Unknown URL {managed_release_notes_url}')

    managed_release_notes_page_data_list = get_release_notes_page_data_list(unknown_managed_release_notes_urls)
    managed_release_notes_page_data_list.extend(known_managed_release_notes_pages)

    # One time removal of duplicates
    # managed_release_notes_page_data_list = [*set(managed_release_notes_page_data_list)]

    managed_release_notes_page_data_list.sort(key=lambda y: y[1], reverse=True)

    write_yaml('known_managed_release_notes_pages.yaml', managed_release_notes_page_data_list)
    write_html('Managed Release Notes', f'{html_path}/dynatrace_managed_release_notes_history.html', format_html('Release Notes', managed_release_notes_page_data_list))


def process_one_agent_release_notes(one_agent_release_notes_url_list):
    known_one_agent_release_notes_pages = read_yaml('known_one_agent_release_notes_pages.yaml')
    known_one_agent_release_notes_urls = []
    for known_one_agent_release_notes_page in known_one_agent_release_notes_pages:
        known_one_agent_release_notes_urls.append(known_one_agent_release_notes_page[0])

    unknown_one_agent_release_notes_urls = []
    for one_agent_release_notes_url in one_agent_release_notes_url_list:
        if one_agent_release_notes_url not in known_one_agent_release_notes_urls:
            unknown_one_agent_release_notes_urls.append(one_agent_release_notes_url)
            print(f'Unknown URL {one_agent_release_notes_url}')

    one_agent_release_notes_page_data_list = get_release_notes_page_data_list(unknown_one_agent_release_notes_urls)
    one_agent_release_notes_page_data_list.extend(known_one_agent_release_notes_pages)

    # One time removal of duplicates
    # one_agent_release_notes_page_data_list = [*set(one_agent_release_notes_page_data_list)]

    one_agent_release_notes_page_data_list.sort(key=lambda y: y[1], reverse=True)

    write_yaml('known_one_agent_release_notes_pages.yaml', one_agent_release_notes_page_data_list)
    write_html('One Agent Release Notes', f'{html_path}/dynatrace_one_agent_release_notes_history.html', format_html('Release Notes', one_agent_release_notes_page_data_list))


def process_active_gate_release_notes(active_gate_release_notes_url_list):
    known_active_gate_release_notes_pages = read_yaml('known_active_gate_release_notes_pages.yaml')
    known_active_gate_release_notes_urls = []
    for known_active_gate_release_notes_page in known_active_gate_release_notes_pages:
        known_active_gate_release_notes_urls.append(known_active_gate_release_notes_page[0])

    unknown_active_gate_release_notes_urls = []
    for active_gate_release_notes_url in active_gate_release_notes_url_list:
        if active_gate_release_notes_url not in known_active_gate_release_notes_urls:
            unknown_active_gate_release_notes_urls.append(active_gate_release_notes_url)
            print(f'Unknown URL {active_gate_release_notes_url}')

    active_gate_release_notes_page_data_list = get_release_notes_page_data_list(unknown_active_gate_release_notes_urls)
    active_gate_release_notes_page_data_list.extend(known_active_gate_release_notes_pages)

    # One time removal of duplicates
    # active_gate_release_notes_page_data_list = [*set(active_gate_release_notes_page_data_list)]

    active_gate_release_notes_page_data_list.sort(key=lambda y: y[1], reverse=True)

    write_yaml('known_active_gate_release_notes_pages.yaml', active_gate_release_notes_page_data_list)
    write_html('Active Gate Release Notes', f'{html_path}/dynatrace_active_gate_release_notes_history.html', format_html('Release Notes', active_gate_release_notes_page_data_list))


def process():
    blog_url_list, saas_release_notes_url_list, managed_release_notes_url_list, one_agent_release_notes_url_list, active_gate_release_notes_url_list = get_url_lists()

    process_blogs(blog_url_list)
    process_saas_release_notes(saas_release_notes_url_list)
    process_managed_release_notes(managed_release_notes_url_list)
    process_one_agent_release_notes(one_agent_release_notes_url_list)
    process_active_gate_release_notes(active_gate_release_notes_url_list)


if __name__ == '__main__':
    process()
