#
# Extract text from hrefs found in list of urls
#

import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    configuration_file = 'configurations.yaml'
    root_page_list = environment.get_configuration('extract_text_from_urls2_root_page_list', configuration_file=configuration_file)
    if not root_page_list:
        print(f'A value for "root_page_list" must be provided in {configuration_file}')
        exit(1)

    print('Root Page:', root_page_list)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}

    link_list = []
    href_list = []

    for root_page in root_page_list:
        r = requests.get(root_page, headers=headers)

        # print(r.text)

        soup = BeautifulSoup(r.text, 'html.parser')

        for link in soup.find_all('a'):
            # print(link.text)
            # link_str = str(link)
            # print(link_str)
            if link.has_attr('href'):
                href = link['href']
                if href.startswith('https://readbrazilianportuguese.com/') and href.endswith('/'):
                    if 'page' not in href and '.com/20' not in href and '.com/category' not in href and '.com/contact-us/' not in href and '.com/disclaimer' not in href and '.com/listening-c' not in href  and '-exercises/' not in href and '.com/privacy' not in href and '.com/terms-conditions' not in href:
                        if href != 'https://readbrazilianportuguese.com/':
                            href_list.append(href)
                            a = link.text
                            if a != 'Read More' and a != '':
                                link_list.append(f'<a href="{link["href"]}">{a}</a>')

        # href = link.get('href')
        # if href:
        #     if 'Read More' in href:
            # href_list.append(href)

    unique_hrefs = remove_duplicates(sorted(href_list))
    unique_links = remove_duplicates(sorted(link_list))

    for unique_href in unique_hrefs:
        # print(unique_href)

        r = requests.get(unique_href, headers=headers)
        # print(r.text)
        # exit(9999)
        soup = BeautifulSoup(r.text, 'html.parser')

        for title in soup.find_all('title'):
            print(title.text.strip())

        print('')

        for div in soup.find_all('div', itemprop="text"):
            # div_p = div.find('p').text
            print(div.text.strip())
            print('')

        print('~PG~')

    # print('<pre>')
    # for unique_link in unique_links:
    #     print(unique_link)
    # print('</pre>')


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


if __name__ == '__main__':
    process()
