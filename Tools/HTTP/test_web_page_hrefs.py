#
# Extract a list of unique hrefs from a web page
#

import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    configuration_file = 'configurations.yaml'
    root_page = environment.get_configuration('root_page', configuration_file=configuration_file)
    if not root_page:
        print(f'A value for "root_page" must be provided in {configuration_file}')
        exit(1)

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    href_list = []
    for link in soup.find_all('a'):
        href = link.get('href')
        href_list.append(href)

    unique_hrefs = remove_duplicates(sorted(href_list))

    for unique_href in unique_hrefs:
        # Only test pages "under" the root
        if unique_href.startswith('/'):
            test(root_page, unique_href)


def test(root_page, href):
    child_page = root_page + href
    r = requests.get(child_page)
    http_status_code = r.status_code
    if http_status_code == 200:
        print(child_page, r.status_code)
    else:
        print(child_page, r.status_code, r.reason, r.text)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


if __name__ == '__main__':
    process()
