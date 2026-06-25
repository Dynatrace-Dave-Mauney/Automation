# Generated with Copilot
#
# Prompts:
# Create python code using beautiful soup to extract the old and new metric keys from this page: https://docs.dynatrace.com/docs/shortlink/built-in-metrics-on-grail.  Store the results in classic_metic_to_grail_metric.yaml as a dictionary.
#
# I have manually fixed the many-to-one mappings, and some other issues to create this version of the yaml:  https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml.  Modify  code to account for multiple classic metrics being mapped to a single gen3 metric.  Modify to account for other issues that were cleaned up manually.  The original yaml is here: https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Tools/HTTP/classic_metric_to_grail_metric.yaml

import csv
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
import yaml
from bs4 import BeautifulSoup


DOCS_URL = (
    "https://docs.dynatrace.com/docs/"
    "analyze-explore-automate/metrics/built-in-metrics-on-grail"
)

# Your manually cleaned / authoritative version
CURATED_YAML_URL = (
    "https://raw.githubusercontent.com/"
    "Dynatrace-Dave-Mauney/Automation/main/"
    "NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml"
)

# Original generated version, useful for comparison / diagnostics
ORIGINAL_YAML_URL = (
    "https://raw.githubusercontent.com/"
    "Dynatrace-Dave-Mauney/Automation/main/"
    "Tools/HTTP/classic_metric_to_grail_metric.yaml"
)


def fetch_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 metric-mapping-sync/1.0"
    }
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.text


def clean_metric_key(value: Any) -> Optional[str]:
    """
    Normalize metric key-ish values.

    Handles common cleanup issues from scraped docs/YAML:
    - None / blank values
    - accidental whitespace/newlines
    - markdown/code formatting
    - duplicated internal whitespace
    - trailing punctuation from prose
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Remove common markdown/code wrappers.
    text = text.strip("`").strip()

    # Collapse whitespace introduced by HTML extraction/YAML formatting.
    text = re.sub(r"\s+", "", text)

    # Strip obvious trailing punctuation that is not valid in Dynatrace metric keys.
    text = text.rstrip(",;")

    # Ignore placeholders / prose / unsupported markers.
    lowered = text.lower()
    if lowered in {
        "n/a",
        "na",
        "none",
        "null",
        "-",
        "unsupported",
        "notavailable",
        "notapplicable",
    }:
        return None

    return text


def looks_like_classic_metric(value: Optional[str]) -> bool:
    if not value:
        return False

    return value.startswith((
        "builtin:",
        "calc:",
        "ext:",
        "custom:",
        "appmon:",
        "func:",
        "uscm.",
        "uacm.",
    ))


def looks_like_grail_metric(value: Optional[str]) -> bool:
    if not value:
        return False

    return value.startswith((
        "dt.",
        "builtin.",      # tolerate older generated forms if present
        "service.",
        "log.",
        "metric.",
        "cloud.",
        "host.",
        "legacy.",
    ))


def add_mapping(
    classic_to_grail: Dict[str, str],
    grail_to_classics: Dict[str, List[str]],
    classic_key: Any,
    grail_key: Any,
    source: str,
    diagnostics: List[Dict[str, Any]],
    authoritative: bool = False,
) -> None:
    classic = clean_metric_key(classic_key)
    grail = clean_metric_key(grail_key)

    if not classic or not grail:
        diagnostics.append({
            "source": source,
            "issue": "blank classic or grail key",
            "classic": classic_key,
            "grail": grail_key,
        })
        return

    if not looks_like_classic_metric(classic):
        diagnostics.append({
            "source": source,
            "issue": "classic key did not look like a classic metric key",
            "classic": classic,
            "grail": grail,
        })
        # Do not return; keep it in case the curated YAML intentionally includes it.

    if not looks_like_grail_metric(grail):
        diagnostics.append({
            "source": source,
            "issue": "grail key did not look like a Grail/gen3 metric key",
            "classic": classic,
            "grail": grail,
        })
        # Do not return; keep it in case the curated YAML intentionally includes it.

    existing = classic_to_grail.get(classic)

    if existing and existing != grail:
        if authoritative:
            diagnostics.append({
                "source": source,
                "issue": "authoritative override changed classic mapping",
                "classic": classic,
                "old_grail": existing,
                "new_grail": grail,
            })
        else:
            diagnostics.append({
                "source": source,
                "issue": "conflicting non-authoritative mapping ignored",
                "classic": classic,
                "existing_grail": existing,
                "ignored_grail": grail,
            })
            return

    classic_to_grail[classic] = grail

    if classic not in grail_to_classics[grail]:
        grail_to_classics[grail].append(classic)


def extract_scraped_mappings_from_docs(html: str) -> List[Dict[str, str]]:
    """
    Extract mappings from the Dynatrace docs tables.

    Returns list of:
      {
        "classic_metric_key": "...",
        "grail_metric_key": "..."
      }
    """
    soup = BeautifulSoup(html, "html.parser")

    mappings = []

    for table in soup.find_all("table"):
        headers = [th.get_text(" ", strip=True) for th in table.find_all("th")]

        if not headers:
            continue

        grail_idx = None
        classic_idx = None

        for idx, header in enumerate(headers):
            normalized_header = header.lower()
            if "metric key" in normalized_header and "grail" in normalized_header:
                grail_idx = idx
            elif "metric key" in normalized_header and "classic" in normalized_header:
                classic_idx = idx

        if grail_idx is None or classic_idx is None:
            continue

        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")

            if len(cols) <= max(grail_idx, classic_idx):
                continue

            grail_key = clean_metric_key(cols[grail_idx].get_text(" ", strip=True))
            classic_cell_text = cols[classic_idx].get_text(" ", strip=True)

            classic_keys = extract_metric_keys_from_cell(classic_cell_text)

            for classic_key in classic_keys:
                mappings.append({
                    "classic_metric_key": classic_key,
                    "grail_metric_key": grail_key,
                })

    return mappings


def extract_metric_keys_from_cell(text: str) -> List[str]:
    """
    Handles single classic metric per cell and multiple classic metrics per cell.

    This is important for manually cleaned many-to-one cases and for docs rows where
    multiple classic keys may appear in one table cell.

    Examples handled:
      builtin:a.b
      builtin:a.b builtin:c.d
      builtin:a.b, builtin:c.d
      - builtin:a.b
      - builtin:c.d
    """
    if not text:
        return []

    normalized = text.replace("\n", " ").replace("\r", " ")

    # Metric keys are generally non-whitespace tokens beginning with known prefixes.
    pattern = r"(?:builtin:|calc:|ext:|custom:|appmon:|func:|uscm\.|uacm\.)[A-Za-z0-9_:#.%\-/]+"

    keys = re.findall(pattern, normalized)

    cleaned = []
    for key in keys:
        key = clean_metric_key(key)
        if key and key not in cleaned:
            cleaned.append(key)

    return cleaned


def normalize_yaml_to_pairs(data: Any) -> List[Tuple[str, str]]:
    """
    Convert several likely YAML shapes into a flat list of:
      (classic_metric_key, grail_metric_key)

    Supported shapes:

    1. Classic-to-Grail dictionary:
       builtin:host.cpu.usage: dt.host.cpu.usage

    2. Grail-to-classics dictionary:
       dt.runtime.jvm.gc.collection_time:
         - builtin:tech.jvm.memory.gc.collectionTime
         - builtin:tech.jvm.memory.pool.collectionTime

    3. List of dictionaries:
       - classic_metric_key: builtin:x
         grail_metric_key: dt.x

    4. List of dictionaries where one Grail key has many classic keys:
       - grail_metric_key: dt.x
         classic_metric_keys:
           - builtin:a
           - builtin:b

    5. Nested dictionary variants:
       dt.x:
         classic_metric_keys:
           - builtin:a
           - builtin:b

       builtin:a:
         grail_metric_key: dt.x
    """
    pairs: List[Tuple[str, str]] = []

    if data is None:
        return pairs

    if isinstance(data, list):
        for item in data:
            pairs.extend(normalize_yaml_list_item(item))
        return pairs

    if isinstance(data, dict):
        for key, value in data.items():
            key_clean = clean_metric_key(key)

            # Case: classic -> grail string
            if isinstance(value, str):
                value_clean = clean_metric_key(value)

                if looks_like_classic_metric(key_clean) and looks_like_grail_metric(value_clean):
                    pairs.append((key_clean, value_clean))
                elif looks_like_grail_metric(key_clean) and looks_like_classic_metric(value_clean):
                    pairs.append((value_clean, key_clean))
                else:
                    # Best effort fallback. Assume original script generated classic -> grail.
                    pairs.append((key_clean, value_clean))

            # Case: grail -> [classic...]
            elif isinstance(value, list):
                if looks_like_grail_metric(key_clean):
                    for classic in value:
                        classic_clean = clean_metric_key(classic)
                        if classic_clean:
                            pairs.append((classic_clean, key_clean))
                elif looks_like_classic_metric(key_clean):
                    for grail in value:
                        grail_clean = clean_metric_key(grail)
                        if grail_clean:
                            pairs.append((key_clean, grail_clean))

            # Case: nested dictionary
            elif isinstance(value, dict):
                pairs.extend(normalize_nested_yaml_mapping(key_clean, value))

    return pairs


def normalize_yaml_list_item(item: Any) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []

    if not isinstance(item, dict):
        return pairs

    grail = first_present(
        item,
        "grail_metric_key",
        "new_metric_key",
        "gen3_metric_key",
        "metric_key_grail",
        "grail",
        "new",
    )

    classic_single = first_present(
        item,
        "classic_metric_key",
        "old_metric_key",
        "metric_key_classic",
        "classic",
        "old",
    )

    classic_many = first_present(
        item,
        "classic_metric_keys",
        "old_metric_keys",
        "classic_metrics",
        "old_metrics",
    )

    if grail and classic_single:
        pairs.append((classic_single, grail))

    if grail and isinstance(classic_many, list):
        for classic in classic_many:
            pairs.append((classic, grail))

    # If this item is actually a one-entry mapping, recurse.
    if not pairs and len(item) == 1:
        pairs.extend(normalize_yaml_to_pairs(item))

    return pairs


def normalize_nested_yaml_mapping(key_clean: Optional[str], value: Dict[str, Any]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []

    grail_nested = first_present(
        value,
        "grail_metric_key",
        "new_metric_key",
        "gen3_metric_key",
        "metric_key_grail",
        "grail",
        "new",
    )

    classic_single = first_present(
        value,
        "classic_metric_key",
        "old_metric_key",
        "metric_key_classic",
        "classic",
        "old",
    )

    classic_many = first_present(
        value,
        "classic_metric_keys",
        "old_metric_keys",
        "classic_metrics",
        "old_metrics",
    )

    # key is Grail, nested classic list
    if looks_like_grail_metric(key_clean):
        if classic_single:
            pairs.append((classic_single, key_clean))

        if isinstance(classic_many, list):
            for classic in classic_many:
                pairs.append((classic, key_clean))

    # key is Classic, nested Grail value
    if looks_like_classic_metric(key_clean) and grail_nested:
        pairs.append((key_clean, grail_nested))

    # Nested explicit pair
    if grail_nested and classic_single:
        pairs.append((classic_single, grail_nested))

    if grail_nested and isinstance(classic_many, list):
        for classic in classic_many:
            pairs.append((classic, grail_nested))

    return pairs


def first_present(mapping: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def load_yaml_pairs_from_url(url: str) -> List[Tuple[str, str]]:
    text = fetch_text(url)
    data = yaml.safe_load(text)
    return normalize_yaml_to_pairs(data)


def build_mapping_indexes(
    scraped_pairs: Iterable[Tuple[str, str]],
    original_yaml_pairs: Iterable[Tuple[str, str]],
    curated_yaml_pairs: Iterable[Tuple[str, str]],
) -> Tuple[Dict[str, str], Dict[str, List[str]], List[Dict[str, Any]]]:
    """
    Merge order:
      1. scraped docs mappings
      2. original generated YAML mappings
      3. curated YAML mappings, authoritative override

    The curated YAML wins when the same classic key has a corrected Grail mapping.
    """
    diagnostics: List[Dict[str, Any]] = []

    classic_to_grail: Dict[str, str] = {}
    grail_to_classics: Dict[str, List[str]] = defaultdict(list)

    for classic, grail in scraped_pairs:
        add_mapping(
            classic_to_grail,
            grail_to_classics,
            classic,
            grail,
            source="docs scrape",
            diagnostics=diagnostics,
            authoritative=False,
        )

    for classic, grail in original_yaml_pairs:
        add_mapping(
            classic_to_grail,
            grail_to_classics,
            classic,
            grail,
            source="original yaml",
            diagnostics=diagnostics,
            authoritative=False,
        )

    for classic, grail in curated_yaml_pairs:
        add_mapping(
            classic_to_grail,
            grail_to_classics,
            classic,
            grail,
            source="curated yaml",
            diagnostics=diagnostics,
            authoritative=True,
        )

    # Rebuild reverse index after authoritative overrides to avoid stale reverse entries.
    rebuilt_grail_to_classics: Dict[str, List[str]] = defaultdict(list)

    for classic, grail in sorted(classic_to_grail.items()):
        rebuilt_grail_to_classics[grail].append(classic)

    return classic_to_grail, dict(rebuilt_grail_to_classics), diagnostics


def write_classic_to_grail_yaml(classic_to_grail: Dict[str, str], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            dict(sorted(classic_to_grail.items())),
            f,
            sort_keys=False,
            allow_unicode=True,
            width=160,
        )


def write_grail_to_classics_yaml(grail_to_classics: Dict[str, List[str]], path: str) -> None:
    normalized = {
        grail: sorted(classics)
        for grail, classics in sorted(grail_to_classics.items())
    }

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            normalized,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=160,
        )


def write_csv(classic_to_grail: Dict[str, str], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "classic_metric_key",
                "grail_metric_key",
            ],
        )
        writer.writeheader()

        for classic, grail in sorted(classic_to_grail.items()):
            writer.writerow({
                "classic_metric_key": classic,
                "grail_metric_key": grail,
            })


def write_diagnostics(diagnostics: List[Dict[str, Any]], path: str) -> None:
    if not diagnostics:
        diagnostics = [{"issue": "no diagnostics"}]

    # Gather all possible fields so the CSV does not drop useful details.
    fields = sorted({k for row in diagnostics for k in row.keys()})

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(diagnostics)


def main() -> None:
    docs_html = fetch_text(DOCS_URL)

    scraped_records = extract_scraped_mappings_from_docs(docs_html)
    scraped_pairs = [
        (row["classic_metric_key"], row["grail_metric_key"])
        for row in scraped_records
    ]

    original_pairs = load_yaml_pairs_from_url(ORIGINAL_YAML_URL)
    curated_pairs = load_yaml_pairs_from_url(CURATED_YAML_URL)

    classic_to_grail, grail_to_classics, diagnostics = build_mapping_indexes(
        scraped_pairs=scraped_pairs,
        original_yaml_pairs=original_pairs,
        curated_yaml_pairs=curated_pairs,
    )

    write_classic_to_grail_yaml(
        classic_to_grail,
        "classic_metric_to_grail_metric.normalized.yaml",
    )

    write_grail_to_classics_yaml(
        grail_to_classics,
        "grail_metric_to_classic_metrics.normalized.yaml",
    )

    write_csv(
        classic_to_grail,
        "classic_metric_to_grail_metric.normalized.csv",
    )

    write_diagnostics(
        diagnostics,
        "metric_mapping_diagnostics.csv",
    )

    many_to_one = {
        grail: classics
        for grail, classics in grail_to_classics.items()
        if len(classics) > 1
    }

    print(f"Classic -> Grail mappings: {len(classic_to_grail)}")
    print(f"Grail -> Classic mappings: {len(grail_to_classics)}")
    print(f"Many classic -> one Grail mappings: {len(many_to_one)}")
    print(f"Diagnostics rows: {len(diagnostics)}")

    print("\nSample many-to-one mappings:")
    for grail, classics in list(sorted(many_to_one.items()))[:10]:
        print(f"\n{grail}")
        for classic in classics:
            print(f"  - {classic}")


if __name__ == "__main__":
    main()
