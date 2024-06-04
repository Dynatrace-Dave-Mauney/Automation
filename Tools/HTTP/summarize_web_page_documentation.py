#
# Extract a list of unique items from a web page
#

import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    root_page = "https://docs.dynatrace.com/docs/platform/semantic-dictionary/model/bizevents"
    root_page = "https://docs.dynatrace.com/docs/platform/semantic-dictionary/model/dt-system-events"
    root_page = "https://docs.dynatrace.com/docs/platform/semantic-dictionary/model/davis"
    root_page = "https://docs.dynatrace.com/docs/shortlink/semantic-dictionary-topology"

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    headings = soup.find_all("h2", class_="sc-5765a625-0 dplWxV")
    # for heading in headings:
    #     print(heading.text)


    tables = soup.find_all("table", class_="sc-6dde538b-1 gjGoxB")

    index = 0
    for table in tables:
        # print(table.text)
        # if 'BILLING_USAGE_EVENT' not in table.text and 'LIMA_CLIENT' not in table.text and 'LIMA_USAGE_STREAM' not in table.text and 'Runtime Vulnerability Protection' not in table.text:
        # For 2nd root page
        # if 'ValueDescription' not in table.text:
        # For 3rd root page
        # if 'event.status' in table.text:
        # For 4th root page
        if 'Examples' in table.text:
            print('')
            print(headings[index].text)
            index += 1
        # print(table)
            for td in table.select('tbody > tr > td:nth-child(1)'):
                print(td.text)


if __name__ == '__main__':
    process()
