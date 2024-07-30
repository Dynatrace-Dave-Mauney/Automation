#
# Extract a list of unique items from a web page
#

import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    root_page = "https://docs.dynatrace.com/docs/observe-and-explore/metrics/built-in-metrics-on-grail"

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    tables = soup.find_all("table", class_="sc-6dde538b-1 gjGoxB")

    metric_list = []

    for table in tables:
        if 'Metric key (Grail)' in table.text:
            for td in table.select('tbody > tr > td:nth-child(1)'):
                if td.text.startswith('dt.'):
                    # print(td.text)
                    metric_list.append(td.text)

    for metric in sorted(metric_list):
        print(metric)


if __name__ == '__main__':
    process()
