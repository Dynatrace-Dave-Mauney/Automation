#!/usr/bin/env python3

"""
convert_verbose_metric_mapping.py

Reads:
    verbose_classic_metric_to_grail_metric.yaml (JSON-compatible YAML)

Writes:
    classic_metric_to_grail_metric.yaml

Output format:
    classic_metric: gen3_metric
"""

import os
import sys
import yaml
from typing import Dict, Any, List


INPUT_FILE = "verbose_classic_metric_to_grail_metric.yaml"
OUTPUT_FILE = "classic_metric_to_grail_metric.yaml"


def load_yaml(file_path: str) -> Any:
    """Load YAML (also supports JSON since it's valid YAML)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_successful_mappings(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract only the successful_mappings list."""
    if not isinstance(data, dict):
        raise ValueError("Expected top-level YAML to be a dictionary")

    mappings = data.get("successful_mappings")

    if not isinstance(mappings, list):
        raise ValueError("'successful_mappings' is missing or not a list")

    return mappings


def build_mapping(records: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Build classic -> gen3 mapping.
    Only includes valid entries.
    """

    mapping = {}

    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        classic = record.get("classic_metric")
        gen3 = record.get("gen3_metric")

        if not classic or not gen3:
            print(f"[WARN] Skipping invalid entry at index {idx}")
            continue

        if classic in mapping and mapping[classic] != gen3:
            print(f"[WARN] Conflict for '{classic}': '{mapping[classic]}' -> '{gen3}' (overwriting)")

        mapping[classic] = gen3

    return mapping


def write_yaml(mapping: Dict[str, str], file_path: str) -> None:
    """Write simplified YAML dictionary."""
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(
            mapping,
            f,
            default_flow_style=False,
            sort_keys=True,
            allow_unicode=True
        )


def main():
    try:
        print(f"Reading: {INPUT_FILE}")
        data = load_yaml(INPUT_FILE)

        records = extract_successful_mappings(data)
        print(f"Successful mappings found: {len(records)}")

        mapping = build_mapping(records)
        print(f"Valid mappings extracted: {len(mapping)}")

        write_yaml(mapping, OUTPUT_FILE)

        print(f"✅ Output written to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
