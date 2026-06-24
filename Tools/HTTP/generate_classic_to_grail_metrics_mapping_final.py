# Generated with Copilot
# Create python code using beautiful soup to extract the old and new metric keys from this page: https://docs.dynatrace.com/docs/shortlink/built-in-metrics-on-grail.  Store the results in classic_metic_to_grail_metric.yaml as a dictionary.

import requests
from bs4 import BeautifulSoup
import yaml


URL = "https://docs.dynatrace.com/docs/analyze-explore-automate/metrics/built-in-metrics-on-grail"


def fetch_page(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text


def extract_metric_mappings(html):
    soup = BeautifulSoup(html, "lxml")

    mappings = {}

    # Find all tables (page has many sections)
    tables = soup.find_all("table")

    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        # We only care about tables that have both columns
        if not headers:
            continue

        try:
            grail_idx = headers.index("Metric key (Grail)")
            classic_idx = headers.index("Metric key (Classic)")
        except ValueError:
            continue  # Not a mapping table

        # Parse rows
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) <= max(grail_idx, classic_idx):
                continue

            grail_key = cells[grail_idx].get_text(strip=True)
            classic_key = cells[classic_idx].get_text(strip=True)

            if grail_key and classic_key:
                mappings[classic_key] = grail_key

    return mappings


def write_yaml(data, filename="classic_metric_to_grail_metric.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            sort_keys=True,
            allow_unicode=True
        )


def main():
    html = fetch_page(URL)
    mappings = extract_metric_mappings(html)

    print(f"Extracted {len(mappings)} metric mappings")

    write_yaml(mappings)


if __name__ == "__main__":
    main()