#
# Extract a sorted list of permissions from the documentation page
#

import requests
from bs4 import BeautifulSoup
from Reuse import environment


def process():
    root_page = "https://docs.dynatrace.com/docs/shortlink/iam-policystatements"

    r = requests.get(root_page)
    soup = BeautifulSoup(r.text, 'html.parser')

    headings = soup.find_all("h3", class_="sc-19276467-0 iTtZJA")

    heading_list = []
    for heading in headings:
        heading_list.append(heading.text)

    for heading in sorted(heading_list):
        print(heading)


if __name__ == '__main__':
    process()
