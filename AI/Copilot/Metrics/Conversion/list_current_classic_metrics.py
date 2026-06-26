#!/usr/bin/env python3
"""
list_current_classic_metrics.py

Lists currently-written Dynatrace classic metric descriptors using Metrics API v2
GET /api/v2/metrics with the writtenSince parameter, and stores the result in a
stable JSON artifact intended to feed a downstream classic-to-Gen3 metric mapping
process.

Default behavior:
  - Uses metricSelector=builtin:* because Dynatrace built-in metric keys are the
    usual "classic" metric keys used for classic-to-Gen3 mapping work.
  - Uses writtenSince=now-30d to mean "current" unless overridden.
  - Writes current_classic_metrics.json.

Required token scope:
  - metrics.read

Environment variables supported:
  - DT_ENV_URL       Example: https://abc12345.live.dynatrace.com
  - DT_API_TOKEN     Dynatrace API token with metrics.read scope

Examples:
  python list_current_classic_metrics.py \
    --env-url https://abc12345.live.dynatrace.com \
    --api-token "$DT_API_TOKEN" \
    --written-since now-14d \
    --output current_classic_metrics.json

  # Include extension/calculated/custom namespaces too, if desired:
  python list_current_classic_metrics.py \
    --metric-selector 'builtin:*' \
    --metric-selector 'ext:*' \
    --metric-selector 'calc:*' \
    --metric-selector 'custom:*'
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urljoin

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: requests. Install with: pip install requests"
    ) from exc


DEFAULT_FIELDS = ",".join(
    [
        "+lastWritten",
        "+created",
        "+aggregationTypes",
        "+defaultAggregation",
        "+dimensionDefinitions",
        "+entityType",
        "+tags",
        "+metricValueType",
        "+transformations",
        "+rootCauseRelevant",
        "+impactRelevant",
        "+exported",
        "+billable",
    ]
)

# DEFAULT_METRIC_SELECTORS = ["builtin:*"]
DEFAULT_METRIC_SELECTORS = ["*"]
DEFAULT_WRITTEN_SINCE = "now-30d"
DEFAULT_PAGE_SIZE = 500


class DynatraceMetricsError(RuntimeError):
    """Raised when the Dynatrace Metrics API request fails."""


@dataclass(frozen=True)
class DynatraceConfig:
    env_url: str
    api_token: str
    verify_tls: bool = True
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_sleep_seconds: float = 2.0

    @property
    def metrics_url(self) -> str:
        return urljoin(self.env_url.rstrip("/") + "/", "api/v2/metrics")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_env_url(env_url: str) -> str:
    env_url = (env_url or "").strip()
    if not env_url:
        raise ValueError("Dynatrace environment URL is required.")
    if not env_url.startswith(("https://", "http://")):
        env_url = "https://" + env_url
    return env_url.rstrip("/")


def metric_sort_key(metric: Dict[str, Any]) -> Tuple[str, str]:
    return (str(metric.get("metricId", "")), str(metric.get("displayName", "")))


def dedupe_metrics(metrics: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate metrics by metricId while preserving the richest descriptor."""
    by_id: Dict[str, Dict[str, Any]] = {}
    for metric in metrics:
        metric_id = metric.get("metricId")
        if not metric_id:
            continue
        current = by_id.get(metric_id)
        if current is None:
            by_id[metric_id] = metric
            continue
        # Keep the descriptor with more populated top-level fields.
        new_score = sum(1 for value in metric.values() if value not in (None, "", [], {}))
        old_score = sum(1 for value in current.values() if value not in (None, "", [], {}))
        if new_score > old_score:
            by_id[metric_id] = metric
    return sorted(by_id.values(), key=metric_sort_key)


def request_json_with_retries(
    session: requests.Session,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any],
    config: DynatraceConfig,
) -> Dict[str, Any]:
    last_error: Optional[BaseException] = None
    for attempt in range(1, config.max_retries + 1):
        try:
            response = session.get(
                url,
                headers=headers,
                params=params,
                timeout=config.timeout_seconds,
                verify=config.verify_tls,
            )
            if response.status_code in (429, 500, 502, 503, 504):
                retry_after = response.headers.get("Retry-After")
                sleep_seconds = (
                    float(retry_after)
                    if retry_after and retry_after.replace(".", "", 1).isdigit()
                    else config.retry_sleep_seconds * attempt
                )
                time.sleep(sleep_seconds)
                continue
            if not response.ok:
                raise DynatraceMetricsError(
                    f"Dynatrace Metrics API failed: HTTP {response.status_code}: "
                    f"{response.text[:1000]}"
                )
            return response.json()
        except (requests.RequestException, json.JSONDecodeError, DynatraceMetricsError) as exc:
            last_error = exc
            if attempt < config.max_retries:
                time.sleep(config.retry_sleep_seconds * attempt)
                continue
            break
    raise DynatraceMetricsError(f"Dynatrace Metrics API request failed: {last_error}")


def fetch_metrics_for_selector(
    config: DynatraceConfig,
    metric_selector: str,
    written_since: str,
    fields: str = DEFAULT_FIELDS,
    page_size: int = DEFAULT_PAGE_SIZE,
    written_since_mode: str = "INCLUDE",
) -> Tuple[List[Dict[str, Any]], List[str], Optional[int]]:
    """
    Fetch all matching metric descriptors for one metricSelector.

    Important API pagination rule:
      After nextPageKey is returned, subsequent calls must send only nextPageKey;
      all other query parameters must be omitted.
    """
    headers = {
        "Authorization": f"Api-Token {config.api_token}",
        "Accept": "application/json",
    }
    metrics: List[Dict[str, Any]] = []
    warnings: List[str] = []
    total_count: Optional[int] = None
    next_page_key: Optional[str] = None

    with requests.Session() as session:
        while True:
            if next_page_key:
                params: Dict[str, Any] = {"nextPageKey": next_page_key}
            else:
                params = {
                    "metricSelector": metric_selector,
                    "writtenSince": written_since,
                    "writtenSinceMode": written_since_mode,
                    "fields": fields,
                    "pageSize": min(max(int(page_size), 1), DEFAULT_PAGE_SIZE),
                }

            payload = request_json_with_retries(
                session=session,
                url=config.metrics_url,
                headers=headers,
                params=params,
                config=config,
            )
            metrics.extend(payload.get("metrics", []))
            warnings.extend(payload.get("warnings", []) or [])
            if total_count is None and isinstance(payload.get("totalCount"), int):
                total_count = payload["totalCount"]

            next_page_key = payload.get("nextPageKey")
            if not next_page_key:
                break

    return metrics, warnings, total_count


def build_output_document(
    *,
    env_url: str,
    written_since: str,
    written_since_mode: str,
    metric_selectors: Sequence[str],
    raw_total_counts: Dict[str, Optional[int]],
    metrics: Sequence[Dict[str, Any]],
    warnings: Sequence[str],
) -> Dict[str, Any]:
    return {
        "schemaVersion": "1.0",
        "artifactType": "dynatrace.current_classic_metrics",
        "generatedAtUtc": utc_now_iso(),
        "source": {
            "api": "Metrics API v2 GET /api/v2/metrics",
            "environmentUrl": env_url,
            "writtenSince": written_since,
            "writtenSinceMode": written_since_mode,
            "metricSelectors": list(metric_selectors),
            "rawTotalCountsBySelector": raw_total_counts,
        },
        "summary": {
            "metricCount": len(metrics),
            "warningsCount": len(warnings),
        },
        "warnings": list(warnings),
        "metrics": list(metrics),
        "mappingCandidates": [
            {
                "classicMetricKey": metric.get("metricId"),
                "displayName": metric.get("displayName"),
                "unit": metric.get("unit"),
                "lastWritten": metric.get("lastWritten"),
                "entityType": metric.get("entityType"),
                "dimensions": [
                    dim.get("key")
                    for dim in metric.get("dimensionDefinitions", []) or []
                    if isinstance(dim, dict) and dim.get("key")
                ],
                "defaultAggregation": metric.get("defaultAggregation"),
                "aggregationTypes": metric.get("aggregationTypes"),
                "exportedToGrail": metric.get("exported"),
                "gen3MetricKey": None,
                "mappingStatus": "unmapped",
                "mappingNotes": None,
            }
            for metric in metrics
        ],
    }


def write_json(path: Path, document: Dict[str, Any]) -> None:
    path.write_text(json.dumps(document, indent=2, sort_keys=False), encoding="utf-8")


def write_jsonl(path: Path, metrics: Sequence[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for metric in metrics:
            fh.write(json.dumps(metric, sort_keys=False) + "\n")


def write_mapping_seed_csv(path: Path, mapping_candidates: Sequence[Dict[str, Any]]) -> None:
    fieldnames = [
        "classicMetricKey",
        "gen3MetricKey",
        "mappingStatus",
        "displayName",
        "unit",
        "lastWritten",
        "entityType",
        "dimensions",
        "defaultAggregation",
        "aggregationTypes",
        "exportedToGrail",
        "mappingNotes",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in mapping_candidates:
            flattened = dict(row)
            for key in ("entityType", "dimensions", "defaultAggregation", "aggregationTypes"):
                flattened[key] = json.dumps(flattened.get(key), sort_keys=True)
            writer.writerow(flattened)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "List current Dynatrace classic metrics using Metrics API v2 writtenSince "
            "and write a JSON artifact for downstream mapping."
        )
    )
    parser.add_argument(
        "--env-url",
        default=os.getenv("DT_ENV_URL"),
        help="Dynatrace environment base URL. Can also use DT_ENV_URL.",
    )
    parser.add_argument(
        "--api-token",
        default=os.getenv("DT_API_TOKEN"),
        help="Dynatrace API token with metrics.read scope. Can also use DT_API_TOKEN.",
    )
    parser.add_argument(
        "--written-since",
        default=DEFAULT_WRITTEN_SINCE,
        help=(
            "Metrics API writtenSince value. Examples: now-30d, now-14d, "
            "2026-06-01T00:00:00Z, or UTC milliseconds. Default: now-30d."
        ),
    )
    parser.add_argument(
        "--written-since-mode",
        default="INCLUDE",
        choices=["INCLUDE", "EXCLUDE"],
        help="How writtenSince is applied. Default: INCLUDE.",
    )
    parser.add_argument(
        "--metric-selector",
        action="append",
        dest="metric_selectors",
        default=None,
        help=(
            "Metric selector to include. Repeat for multiple selectors. "
            "Default: builtin:*"
        ),
    )
    parser.add_argument(
        "--fields",
        default=DEFAULT_FIELDS,
        help="Metrics API fields parameter. Default includes mapping-relevant metadata.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help="Page size for first request of each selector. Max API page size is 500.",
    )
    parser.add_argument(
        "--output",
        default="current_classic_metrics.json",
        help="Output JSON artifact path.",
    )
    parser.add_argument(
        "--jsonl-output",
        default=None,
        help="Optional JSONL output path containing one raw metric descriptor per line.",
    )
    parser.add_argument(
        "--mapping-csv-output",
        default=None,
        help="Optional CSV seed file for manual metric mapping review.",
    )
    parser.add_argument(
        "--include-extension-and-custom",
        action="store_true",
        help=(
            "Convenience flag to include ext:*, calc:*, custom:*, and func:* in "
            "addition to builtin:* unless --metric-selector is explicitly provided."
        ),
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification. Not recommended.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=60,
        help="HTTP request timeout in seconds.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    try:
        env_url = normalize_env_url(args.env_url)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not args.api_token:
        print("ERROR: API token is required via --api-token or DT_API_TOKEN.", file=sys.stderr)
        return 2

    if args.metric_selectors:
        metric_selectors = args.metric_selectors
    elif args.include_extension_and_custom:
        metric_selectors = ["builtin:*", "ext:*", "calc:*", "custom:*", "func:*"]
    else:
        metric_selectors = DEFAULT_METRIC_SELECTORS

    config = DynatraceConfig(
        env_url=env_url,
        api_token=args.api_token,
        verify_tls=not args.insecure,
        timeout_seconds=args.timeout_seconds,
    )

    all_metrics: List[Dict[str, Any]] = []
    all_warnings: List[str] = []
    raw_total_counts: Dict[str, Optional[int]] = {}

    for selector in metric_selectors:
        metrics, warnings, total_count = fetch_metrics_for_selector(
            config=config,
            metric_selector=selector,
            written_since=args.written_since,
            fields=args.fields,
            page_size=args.page_size,
            written_since_mode=args.written_since_mode,
        )
        all_metrics.extend(metrics)
        all_warnings.extend(warnings)
        raw_total_counts[selector] = total_count

    metrics = dedupe_metrics(all_metrics)
    all_warnings = sorted(set(all_warnings))

    document = build_output_document(
        env_url=env_url,
        written_since=args.written_since,
        written_since_mode=args.written_since_mode,
        metric_selectors=metric_selectors,
        raw_total_counts=raw_total_counts,
        metrics=metrics,
        warnings=all_warnings,
    )

    output_path = Path(args.output)
    write_json(output_path, document)

    if args.jsonl_output:
        write_jsonl(Path(args.jsonl_output), metrics)

    if args.mapping_csv_output:
        write_mapping_seed_csv(Path(args.mapping_csv_output), document["mappingCandidates"])

    print(
        json.dumps(
            {
                "output": str(output_path),
                "metricCount": len(metrics),
                "writtenSince": args.written_since,
                "metricSelectors": metric_selectors,
                "warningsCount": len(all_warnings),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
