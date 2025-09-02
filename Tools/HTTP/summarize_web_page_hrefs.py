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
    # for link in soup.find_all('h1', class_='entry-title'):
    #     print(link)
        href = link.get('href')
        # if href and 'https://' in href and '/20' in href:
            # print(href)
        href_list.append(href)

    print(href_list)
    unique_hrefs = remove_duplicates(sorted(href_list))

    for unique_href in unique_hrefs:
        print(unique_href)


def remove_duplicates(any_list):
    new_list = []
    [new_list.append(x) for x in any_list if x not in new_list]
    return new_list


if __name__ == '__main__':
    process()
