import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    configuration_file = 'configurations.yaml'
    root_page_list = environment.get_configuration('root_page_list', configuration_file=configuration_file)
    if not root_page_list:
        print(f'A value for "root_page_list" must be provided in {configuration_file}')
        exit(1)

    print('Root Page:', root_page_list)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}

    for root_page in root_page_list:
        r = requests.get(root_page, headers=headers)

        soup = BeautifulSoup(r.text, 'html.parser')

        for link in soup.find_all('li'):
            vocab = link.find('span', class_='vocab').text
            definition = link.find('span', class_='definition').text.replace('(', '').replace(')', '')
            print(vocab + '\t' + definition)


if __name__ == '__main__':
    process()
