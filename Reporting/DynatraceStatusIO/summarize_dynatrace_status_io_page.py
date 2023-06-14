#
# Summarize the Dynatrace Status IO Page.
#
# This is an example that is currently configured for a specific customer and would need to be customized per customer.
#

import requests
from bs4 import BeautifulSoup


def summarize_status_io_page():
    page = requests.get('https://dynatrace.status.io')
    soup = BeautifulSoup(page.text, 'html.parser')

    overall_status = soup.find('strong', id='statusbar_text').text

    print(f'dynatrace.status.io overall_status is currently "{overall_status}"')

    for row in soup.find_all('div', class_='row'):
        # print(row)
        component_name = row.find('p', class_='component_name')
        if component_name and component_name.text == 'AWS - Cluster 37 in US West Oregon':
            component_status = row.find('p', class_='pull-right component-status')
            print(f'"AWS - Cluster 37 in US West Oregon" status is currently "{component_status.text}"')

    for div in soup.find_all('div', id='statusio_external_services'):
        for row in div.find_all('div', class_='row'):
            for i in row.find_all('i'):
                if 'AWS' in i.text:
                    i_class = i.get('class')
                    if 'fa-check' in i_class:
                        print(f'{i.text.strip()} is healthy')
                    else:
                        print(f'{i.text.strip()} is unhealthy')


def main():
    print('Dynatrace Status IO Page Summary')
    summarize_status_io_page()


if __name__ == '__main__':
    main()

