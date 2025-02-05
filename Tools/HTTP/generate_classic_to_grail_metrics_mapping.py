#
# Extract a sorted list of grail metrics from the documentation page.
# The grail metric name is followed by a delimiter of ": " and the classic metric name.
# Metrics that map to more than one classic metric are not included.
# Only "one to one" mappings are included.
#

import requests
from bs4 import BeautifulSoup
# from Reuse import environment


def process():
    root_page1 = "https://docs.dynatrace.com/docs/shortlink/built-in-metrics-on-grail"
    root_page2 = 'https://docs.dynatrace.com/docs/shortlink/host-metrics'

    r = requests.get(root_page1)
    soup = BeautifulSoup(r.text, 'html.parser')

    classic_metrics_to_grail_metrics_dict = {}
    metric_map_list = []

    # list all the cells in the rows.
    # listing all rows did not work for some reason.
    divs = soup.find_all("div", class_="strato-table-custom-cell-wrapper")

    for div in divs:
        if div.text.startswith('dt.'):
            metric_map = div.text
        else:
            if div.text.startswith('builtin:'):
                metric_map += f': {div.text}'
                # suppress output for metrics that have a "many to one" mapping
                # if metric_map.startswith('dt.') and 'builtin:' in metric_map and div.text.count('builtin:') == 1:
                # print(metric_map)
                metric_map_list.append(metric_map)
                metric_map = ""

    for metric_map in metric_map_list:
        # print(metric_map)
        if metric_map.count('builtin:') == 1:
            metric_map_splits = metric_map.split(": ")
            classic_metrics_to_grail_metrics_dict[metric_map_splits[1]] = metric_map_splits[0]
        else:
            metric_map_splits = metric_map.split(": ")
            classic_metrics = metric_map_splits[1].split()
            for classic_metric in classic_metrics:
                classic_metrics_to_grail_metrics_dict[classic_metric] = metric_map_splits[0]

    r = requests.get(root_page2)
    soup = BeautifulSoup(r.text, 'html.parser')

    # list all the cells in the rows.
    # listing all rows did not work for some reason.
    divs = soup.find_all("div", class_="strato-table-custom-cell-wrapper")

    for div in divs:
        if div.text.startswith('builtin:'):
            metric_map = div.text
        else:
            if div.text.startswith('dt.'):
                metric_map += f': {div.text}'
                # suppress output for metrics that have a "many to one" mapping
                # if metric_map.startswith('dt.') and 'builtin:' in metric_map and div.text.count('builtin:') == 1:
                # print(metric_map)
                metric_map_list.append(metric_map)
                metric_map = ""

    for metric_map in metric_map_list:
        # print(metric_map)
        if metric_map.count('builtin:') == 1:
            metric_map_splits = metric_map.split(": ")
            classic_metrics_to_grail_metrics_dict[metric_map_splits[1]] = metric_map_splits[0]
        else:
            metric_map_splits = metric_map.split(": ")
            classic_metrics = metric_map_splits[1].split()
            for classic_metric in classic_metrics:
                classic_metrics_to_grail_metrics_dict[classic_metric] = metric_map_splits[0]

    # allow for two-way conversions and for "flipped" keys on pages
    flipped_dictionary = flip_dictionary(classic_metrics_to_grail_metrics_dict)
    for key in flipped_dictionary.keys():
        classic_metrics_to_grail_metrics_dict[key] = flipped_dictionary[key]

    print(classic_metrics_to_grail_metrics_dict)


def flip_dictionary(classic_metrics_to_grail_metrics_dict):
    flipped_dictionary = {}

    for key in classic_metrics_to_grail_metrics_dict.keys():
        value = classic_metrics_to_grail_metrics_dict[key]
        flipped_dictionary[value] = key

    return flipped_dictionary


if __name__ == '__main__':
    process()
