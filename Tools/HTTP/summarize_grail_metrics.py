#
# Extract a sorted list of grail metrics from the documentation page
#

import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    root_page = "https://docs.dynatrace.com/docs/shortlink/built-in-metrics-on-grail"

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    metrics = soup.find_all("div", class_="strato-table-custom-cell-wrapper")

    metric_list = []
    for metric in metrics:
        if metric.text.startswith('dt.'):
            metric_list.append(metric.text)

    for metric in sorted(metric_list):
        print(metric)


if __name__ == '__main__':
    process()
