#
# Extract a list of unique items from a web page
#

import requests
from bs4 import BeautifulSoup
# from Reuse import environment


def process():
    root_page = "https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/dql-best-practices"

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    headings = soup.find_all("h3")

    for heading in headings:
        if heading.text != 'Related topics':
            print(heading.text)


if __name__ == '__main__':
    process()
