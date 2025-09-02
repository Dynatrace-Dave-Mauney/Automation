import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'}

    configuration_file = 'configurations.yaml'
    extract_text_from_urls_input_file = environment.get_configuration('extract_text_from_urls_input_file', configuration_file=configuration_file)
    print('extract_text_from_urls_input_file:', extract_text_from_urls_input_file)

    with open('output.txt', 'w', encoding='utf-8') as outfile:
        with open(extract_text_from_urls_input_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                # print(line.strip())
                r = requests.get(line, headers=headers)
                print(r.text)
                # exit(9999)
                soup = BeautifulSoup(r.text, 'html.parser')

                for title in soup.find_all('title'):
                    print(title.text.strip())
                    print(title.text.strip(), file=outfile)

                print('')

                # for div in soup.find_all('div', translate='no'):
                # for div in soup.find_all('div', class_='entry-content'):
                # for div in soup.find_all('span', class_='AAYkC'):
                # for div in soup.find_all('div', type='paragraph'):
                for div in soup.find_all('span'):
                # div_p = div.find('p').text
                #     print(div.text)

                    line = div.text.strip()
                    print(line)
                    print('')

                    print(line, file=outfile)
                    print('', file=outfile)

                print('~PG~')
                print('~PG~', file=outfile)

if __name__ == '__main__':
    process()
