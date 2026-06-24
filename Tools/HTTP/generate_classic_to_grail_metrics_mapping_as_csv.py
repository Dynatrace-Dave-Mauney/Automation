# Generated with Copilot
# Create python code using beautiful soup to extract the old and new metric keys from this page: https://docs.dynatrace.com/docs/shortlink/built-in-metrics-on-grail.

import requests
from bs4 import BeautifulSoup
import csv

URL = "https://docs.dynatrace.com/docs/analyze-explore-automate/metrics/built-in-metrics-on-grail"

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_metric_mappings(html):
    soup = BeautifulSoup(html, "html.parser")

    mappings = []

    tables = soup.find_all("table")

    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        # Identify relevant tables
        if not any("Grail" in h for h in headers) or not any("Classic" in h for h in headers):
            continue

        grail_idx = None
        classic_idx = None

        for i, h in enumerate(headers):
            if "Grail" in h:
                grail_idx = i
            elif "Classic" in h:
                classic_idx = i

        if grail_idx is None or classic_idx is None:
            continue

        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) <= max(grail_idx, classic_idx):
                continue

            grail_key = cols[grail_idx].get_text(strip=True)
            classic_key = cols[classic_idx].get_text(strip=True)

            mappings.append({
                "new_metric_key": grail_key,
                "old_metric_key": classic_key
            })

    return mappings

def save_to_csv(mappings, filename="metric_mappings.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["new_metric_key", "old_metric_key"])
        writer.writeheader()
        writer.writerows(mappings)

def main():
    html = fetch_page(URL)
    mappings = extract_metric_mappings(html)

    print(f"Extracted {len(mappings)} metric mappings")

    # Print sample
    for m in mappings[:10]:
        print(m)

    save_to_csv(mappings)


if __name__ == "__main__":
    main()