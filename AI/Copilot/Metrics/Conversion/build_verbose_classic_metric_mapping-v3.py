#!/usr/bin/env python3
"""
build_verbose_classic_metric_mapping.py

Build a classic metric -> Grail/Gen3 metric mapping for every metric in current_classic_metrics.json.

Inputs default to Dave Mauney's Automation repo raw URLs:
  - current_classic_metrics.json
  - classic_metric_to_grail_metric.yaml
  - generate_gen3_dashboards.py
  - set_environment.py

Outputs:
  - passed_metric_mapping_report.csv
  - passed_metric_mapping_report.md
  - failed_metric_mapping_report.csv
  - failed_metric_mapping_report.md
  - verbose_classic_metric_to_grail_metric.yaml
  - verbose_classic_metric_to_grail_metric.json
  - metric_mapping_summary.json

Notes:
  - This script uses ONLY the `metricId` key from current_classic_metrics.json
    to identify Classic metrics. It intentionally does not scrape arbitrary strings,
    descriptions, display names, names, IDs, or object keys.
  - Prefix-less custom metrics are included because whatever appears in metricId
    is treated as the authoritative Classic metric key.
  - This script validates candidates by running a low-cost DQL `timeseries` query.
  - Successful validation means the DQL Query API accepted the metric key and returned
    result metadata according to the checks below. It does not guarantee useful/non-empty
    data beyond the selected timeframe and response checks.
  - It intentionally records every attempted Gen3 metric key for auditability.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

try:
    from Reuse import environment  # noqa: F401 - retained for compatibility when run inside the repo
except ImportError:
    environment = None  # type: ignore[assignment]

try:
    import requests
except ImportError as e:
    raise SystemExit("Missing dependency: requests. Install with: pip install requests") from e

try:
    import yaml
except ImportError as e:
    raise SystemExit("Missing dependency: PyYAML. Install with: pip install pyyaml") from e


DEFAULT_CURRENT_CLASSIC_METRICS_URL = "https://raw.githubusercontent.com/Dynatrace-Dave-Mauney/Automation/refs/heads/main/AI/Copilot/Metrics/Conversion/current_classic_metrics.json"
DEFAULT_MAPPING_YAML_URL = "https://raw.githubusercontent.com/Dynatrace-Dave-Mauney/Automation/refs/heads/main/AI/Copilot/Metrics/Conversion/classic_metric_to_grail_metric.yaml"
DEFAULT_GENERATOR_URL = "https://raw.githubusercontent.com/Dynatrace-Dave-Mauney/Automation/refs/heads/main/AI/Copilot/Dashboards/Generation/generate_gen3_dashboards.py"
DEFAULT_SET_ENVIRONMENT_URL = "https://raw.githubusercontent.com/Dynatrace-Dave-Mauney/Automation/refs/heads/main/AI/Examples/set_environment.py"

# Keep the field name exactly as requested.
CLASSIC_METRIC_ID_FIELD = "metricId"


@dataclass
class Attempt:
    gen3_metric: str
    source: str
    dql: str
    passed: bool
    status_code: Optional[int] = None
    error: Optional[str] = None
    query_status: Optional[str] = None


@dataclass
class MetricResult:
    classic_metric: str
    status: str
    gen3_metric: str
    attempts: List[Attempt]


def fetch_text(location: str, timeout: int = 60) -> str:
    """Fetch a URL or read a local file path."""
    if re.match(r"^https?://", location, re.I):
        resp = requests.get(location, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    return Path(location).read_text(encoding="utf-8")


def load_json(location: str) -> Any:
    return json.loads(fetch_text(location))


def load_yaml(location: str) -> Any:
    text = fetch_text(location)
    data = yaml.safe_load(text)
    return data if data is not None else {}


def load_current_classic_metricIds(data: Any) -> List[str]:
    """Load Classic metric keys using ONLY the `metricId` key.

    This function is intentionally strict. It does not infer metric keys from:
      - metricId / metricKey / key / id / metric / name
      - displayName / description
      - object keys
      - any arbitrary string values

    Supported shapes:
      1. [{"metricId": "..."}, ...]
      2. {"metrics": [{"metricId": "..."}, ...]}
      3. {"items": [{"metricId": "..."}, ...]}
      4. {"data": [{"metricId": "..."}, ...]}
      5. {"result": [{"metricId": "..."}, ...]}
      6. nested combinations of the above containers

    Every non-empty string found in `metricId` is included, including prefix-less
    custom metrics such as `orders.total.count` or even `latency`.
    """
    metrics: List[str] = []

    def add_metricId(value: Any) -> None:
        if isinstance(value, str):
            metric = value.strip()
            if metric:
                metrics.append(metric)

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            if CLASSIC_METRIC_ID_FIELD in value:
                add_metricId(value[CLASSIC_METRIC_ID_FIELD])

            # Recurse only into known containers to avoid accidental scraping of
            # metadata/details while still supporting common wrapper shapes.
            for container in ("metrics", "items", "data", "result"):
                nested = value.get(container)
                if isinstance(nested, (list, tuple, Mapping)):
                    walk(nested)

        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    walk(data)
    return dedupe(metrics)


# Backward-compatible name used by the rest of the script.
def flatten_metric_keys(data: Any) -> List[str]:
    """Return every Classic metric from current_classic_metrics.json using metricId only."""
    return load_current_classic_metricIds(data)


def normalize_mapping_yaml(data: Any) -> Dict[str, List[str]]:
    """Normalize mapping YAML into classic_metric -> [grail candidates]."""
    mapping: Dict[str, List[str]] = {}

    def put(classic: Any, grail: Any) -> None:
        if not classic:
            return
        classic_s = str(classic).strip()
        vals: List[str] = []
        if isinstance(grail, str):
            vals = [grail]
        elif isinstance(grail, Sequence) and not isinstance(grail, (bytes, bytearray, str)):
            vals = [str(x) for x in grail if x]
        elif isinstance(grail, Mapping):
            for key in (
                "grail", "grail_metric", "gen3", "gen3_metric", "to", "to_grail",
                "to_grail_metric", "metric_key_grail", "Metric key (Grail)",
            ):
                if key in grail:
                    candidate = grail[key]
                    if isinstance(candidate, list):
                        vals.extend(str(x) for x in candidate if x)
                    elif candidate:
                        vals.append(str(candidate))
            classic2 = grail.get("classic") or grail.get("classic_metric") or grail.get("from") or grail.get("Metric key (Classic)") or grail.get("metricId")
            grail2 = grail.get("grail") or grail.get("grail_metric") or grail.get("Metric key (Grail)")
            if classic2 and grail2:
                classic_s = str(classic2).strip()
                vals.append(str(grail2))
        vals = [v.strip() for v in vals if str(v).strip()]
        if vals:
            mapping.setdefault(classic_s, [])
            for v in vals:
                if v not in mapping[classic_s]:
                    mapping[classic_s].append(v)

    if isinstance(data, Mapping):
        for list_key in ("mappings", "metrics", "items"):
            if isinstance(data.get(list_key), list):
                for row in data[list_key]:
                    if isinstance(row, Mapping):
                        classic = (
                            row.get("classic") or row.get("classic_metric") or row.get("from")
                            or row.get("Metric key (Classic)") or row.get("metricId")
                        )
                        grail = (
                            row.get("grail") or row.get("grail_metric") or row.get("gen3")
                            or row.get("gen3_metric") or row.get("to") or row.get("to_grail_metric")
                            or row.get("Metric key (Grail)")
                        )
                        put(classic, grail or row)
                return mapping
        for classic, grail in data.items():
            put(classic, grail)
    elif isinstance(data, list):
        for row in data:
            if isinstance(row, Mapping):
                classic = (
                    row.get("classic") or row.get("classic_metric") or row.get("from")
                    or row.get("Metric key (Classic)") or row.get("metricId")
                )
                grail = (
                    row.get("grail") or row.get("grail_metric") or row.get("gen3")
                    or row.get("gen3_metric") or row.get("to") or row.get("to_grail_metric")
                    or row.get("Metric key (Grail)")
                )
                put(classic, grail or row)
    return mapping


def camel_to_snake_segment(segment: str) -> str:
    """Convert camelCase/PascalCase inside one metric-key segment to snake_case."""
    if not segment or segment.startswith("{"):
        return segment
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", segment)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.replace("-", "_").lower()


def snake_metric_key(key: str) -> str:
    return ".".join(camel_to_snake_segment(part) for part in key.split("."))


def dedupe(seq: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in seq:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def quote_metric_for_dql(metric: str) -> str:
    """Backtick metric keys if needed for DQL."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", metric):
        return metric
    return "`" + metric.replace("`", "\\`") + "`"


def heuristic_candidates(classic_metric: str) -> List[Tuple[str, str]]:
    """Candidates deduced from observed Classic -> Grail/Gen3 naming patterns."""
    c = classic_metric.strip()
    candidates: List[Tuple[str, str]] = []

    def add(metric: str, source: str) -> None:
        metric = metric.strip()
        if metric:
            candidates.append((metric, source))
            if metric.endswith(".count"):
                candidates.append((metric[:-6], source + " + strip .count"))
            if metric.endswith(".gauge"):
                candidates.append((metric[:-6], source + " + strip .gauge"))

    # Requested legacy SFM conversion.
    if c.startswith("dsfm:"):
        tail = c[len("dsfm:"):].lstrip(".:")
        add("dt.sfm." + snake_metric_key(tail), "dsfm: -> dt.sfm. + snake_case")
        add("dt.sfm." + tail, "dsfm: -> dt.sfm. only")

    if c.startswith("builtin:tech."):
        tail = c[len("builtin:"):]
        add("legacy." + snake_metric_key(tail), "builtin:tech -> legacy + snake_case")

    if c.startswith("builtin:"):
        tail = c[len("builtin:"):]
        add("dt." + snake_metric_key(tail), "builtin: -> dt. + snake_case")
        add("dt." + tail, "builtin: -> dt. only")

    if c.startswith("ext:"):
        tail = c[len("ext:"):]
        add(snake_metric_key(tail), "ext: removed + snake_case")
        add(tail, "ext: removed only")

    if c.startswith("calc:service."):
        tail = c[len("calc:service."):]
        add("service." + snake_metric_key(tail), "calc:service -> service + snake_case")
        add("service." + tail, "calc:service -> service only")

    if c.startswith("calc:"):
        tail = c[len("calc:"):]
        add(snake_metric_key(tail), "calc: removed + snake_case")

    # Prefix-less custom/OpenTelemetry/Prometheus-style keys are commonly unchanged.
    if not c.startswith(("builtin:", "ext:", "calc:", "dsfm:")):
        add(c, "unchanged")
        add(snake_metric_key(c), "snake_case")

    add(c.replace(":", "."), "colon -> dot fallback")

    out: List[Tuple[str, str]] = []
    seen = set()
    for metric, source in candidates:
        if metric not in seen:
            seen.add(metric)
            out.append((metric, source))
    return out


def build_candidates(classic_metric: str, explicit_mapping: Mapping[str, List[str]]) -> List[Tuple[str, str]]:
    candidates: List[Tuple[str, str]] = []
    for m in explicit_mapping.get(classic_metric, []):
        candidates.append((m, "classic_metric_to_grail_metric.yaml"))
        if m.endswith(".count"):
            candidates.append((m[:-6], "mapping + strip .count"))
        if m.endswith(".gauge"):
            candidates.append((m[:-6], "mapping + strip .gauge"))
    candidates.extend(heuristic_candidates(classic_metric))

    seen = set()
    out: List[Tuple[str, str]] = []
    for metric, source in candidates:
        if metric not in seen:
            seen.add(metric)
            out.append((metric, source))
    return out


def try_load_remote_set_environment(url: str, enabled: bool = True) -> Dict[str, Any]:
    """Try to reuse Dave's set_environment.py if available."""
    if not enabled:
        return {}
    env: Dict[str, Any] = {}
    try:
        source = fetch_text(url)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "set_environment.py"
            p.write_text(source, encoding="utf-8")
            spec = importlib.util.spec_from_file_location("remote_set_environment", str(p))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                fn = getattr(mod, "set_environment", None)
                if callable(fn):
                    try:
                        result = fn()
                    except TypeError:
                        result = fn(None)
                    if isinstance(result, Mapping):
                        env.update(result)
    except Exception as e:
        print(f"WARN: Could not load/use remote set_environment.py: {e}", file=sys.stderr)
    return env


def normalize_base_url(value: str) -> str:
    v = value.strip().rstrip("/")
    if v.endswith("/api"):
        v = v[:-4]
    v = re.sub(r"\.live\.dynatrace\.com/?$", ".apps.dynatrace.com", v)
    return v


def get_auth_config(args: argparse.Namespace) -> Tuple[str, Dict[str, str]]:
    remote_env = try_load_remote_set_environment(args.set_environment_url, enabled=not args.no_remote_set_environment)

    def pick(*names: str) -> Optional[str]:
        for name in names:
            arg_name = name.lower()
            if getattr(args, arg_name, None):
                return getattr(args, arg_name)
            if name in remote_env and remote_env[name]:
                return str(remote_env[name])
            if name in os.environ and os.environ[name]:
                return os.environ[name]
        return None

    base_url = pick(
        "DT_PLATFORM_URL", "DYNATRACE_PLATFORM_URL", "DYNATRACE_APPS_URL",
        "DT_ENVIRONMENT_URL", "DYNATRACE_ENVIRONMENT_URL", "TENANT_URL", "ENVIRONMENT_URL",
    )
    token = pick(
        "DT_PLATFORM_TOKEN", "DYNATRACE_PLATFORM_TOKEN", "DT_OAUTH_TOKEN", "DYNATRACE_OAUTH_TOKEN",
        "DT_TOKEN", "DYNATRACE_TOKEN", "DYNATRACE_API_TOKEN", "API_TOKEN",
    )

    if not base_url:
        raise SystemExit("Missing Dynatrace base URL. Set DT_PLATFORM_URL or DYNATRACE_ENVIRONMENT_URL, or pass --dt-platform-url.")
    if not token:
        raise SystemExit("Missing Dynatrace token. Set DT_PLATFORM_TOKEN / DYNATRACE_TOKEN / DYNATRACE_API_TOKEN, or pass --dt-token.")

    base_url = normalize_base_url(base_url)
    scheme = args.auth_scheme
    if scheme == "auto":
        scheme = "Bearer"
    headers = {
        "Authorization": f"{scheme} {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return base_url, headers


def dql_query_for_metric(metric: str, from_expr: str, to_expr: str) -> str:
    q = quote_metric_for_dql(metric)
    return f"timeseries value = avg({q}), from: {from_expr}, to: {to_expr} | limit 1"


def execute_dql(
    base_url: str,
    headers: Dict[str, str],
    dql: str,
    timeout: int = 45,
    poll_sleep: float = 1.5,
) -> Tuple[bool, Optional[int], Optional[str], Optional[str]]:
    """Run a DQL query using Grail Query API. Returns (passed, status_code, error, query_status)."""
    execute_url = base_url.rstrip("/") + "/platform/storage/query/v1/query:execute"
    payload = {"query": dql, "requestTimeoutMilliseconds": min(timeout * 1000, 60000)}
    try:
        resp = requests.post(execute_url, headers=headers, json=payload, timeout=timeout)
    except Exception as e:
        return False, None, repr(e), None

    status_code = resp.status_code
    text = resp.text[:2000]
    if status_code >= 400:
        return False, status_code, text, None

    try:
        data = resp.json()
    except Exception:
        return True, status_code, None, "UNKNOWN_JSON"

    if status_code == 200:
        result = data.get("result")
        if result:
            records = result.get("records")
            if not records:
                return False, status_code, text, "NO_RECORDS"
            types = result.get("types")
            if not types:
                return False, status_code, text, "NO_TYPES"
        else:
            return False, status_code, text, "NO_RESULT"

    status = str(data.get("state") or data.get("status") or data.get("queryStatus") or "").upper()
    if status in ("SUCCEEDED", "SUCCESS", "FINAL", "DONE", "COMPLETED") or "result" in data or "records" in data:
        return True, status_code, None, status or "SUCCESS"

    request_token = data.get("requestToken") or data.get("request-token") or data.get("token")
    if not request_token:
        return True, status_code, None, status or "ACCEPTED"

    poll_url = base_url.rstrip("/") + "/platform/storage/query/v1/query:poll"
    deadline = time.time() + timeout
    last_status = status
    while time.time() < deadline:
        try:
            poll_resp = requests.get(poll_url, headers=headers, params={"request-token": request_token}, timeout=timeout)
        except Exception as e:
            return False, None, repr(e), last_status
        if poll_resp.status_code >= 400:
            return False, poll_resp.status_code, poll_resp.text[:2000], last_status
        try:
            pdata = poll_resp.json()
        except Exception:
            return True, poll_resp.status_code, None, "UNKNOWN_JSON"
        last_status = str(pdata.get("state") or pdata.get("status") or pdata.get("queryStatus") or "").upper()
        if last_status in ("SUCCEEDED", "SUCCESS", "FINAL", "DONE", "COMPLETED") or "result" in pdata or "records" in pdata:
            return True, poll_resp.status_code, None, last_status or "SUCCESS"
        if last_status in ("FAILED", "ERROR", "CANCELLED", "CANCELED"):
            return False, poll_resp.status_code, json.dumps(pdata)[:2000], last_status
        time.sleep(poll_sleep)
    return False, status_code, f"Timed out; last query status={last_status}", last_status


def validate_metric(
    classic_metric: str,
    candidates: List[Tuple[str, str]],
    base_url: str,
    headers: Dict[str, str],
    args: argparse.Namespace,
) -> MetricResult:
    attempts: List[Attempt] = []
    for gen3, source in candidates:
        dql = dql_query_for_metric(gen3, args.from_expr, args.to_expr)
        if args.dry_run:
            passed, status_code, error, qstatus = False, None, "DRY_RUN: not executed", None
        else:
            passed, status_code, error, qstatus = execute_dql(
                base_url,
                headers,
                dql,
                timeout=args.query_timeout,
                poll_sleep=args.poll_sleep,
            )
        attempts.append(
            Attempt(
                gen3_metric=gen3,
                source=source,
                dql=dql,
                passed=passed,
                status_code=status_code,
                error=error,
                query_status=qstatus,
            )
        )
        if passed:
            return MetricResult(classic_metric=classic_metric, status="PASSED", gen3_metric=gen3, attempts=attempts)
    return MetricResult(classic_metric=classic_metric, status="FAILED", gen3_metric="UNKNOWN:" + classic_metric, attempts=attempts)


def write_csv(path: Path, rows: List[MetricResult]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "classic_metric", "status", "final_gen3_metric", "attempt_number", "attempted_gen3_metric",
            "attempt_source", "passed", "query_status", "http_status", "error", "dql",
        ])
        for r in rows:
            for i, a in enumerate(r.attempts, 1):
                writer.writerow([
                    r.classic_metric,
                    r.status,
                    r.gen3_metric,
                    i,
                    a.gen3_metric,
                    a.source,
                    a.passed,
                    a.query_status or "",
                    a.status_code or "",
                    a.error or "",
                    a.dql,
                ])


def write_markdown(path: Path, title: str, rows: List[MetricResult]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"Metric count: {len(rows)}\n\n")
        for r in rows:
            f.write(f"## `{r.classic_metric}` -> `{r.gen3_metric}` ({r.status})\n\n")
            f.write("| # | Attempted Gen3 metric | Source | Passed | Query status | HTTP | Error |\n")
            f.write("|---:|---|---|---:|---|---:|---|\n")
            for i, a in enumerate(r.attempts, 1):
                err = (a.error or "").replace("|", "\\|").replace("\n", " ")[:300]
                f.write(f"| {i} | `{a.gen3_metric}` | {a.source} | {str(a.passed)} | {a.query_status or ''} | {a.status_code or ''} | {err} |\n")
            f.write("\n")


def write_verbose_yaml(path: Path, passed: List[MetricResult], failed: List[MetricResult]) -> None:
    def convert(r: MetricResult) -> Dict[str, Any]:
        return {
            "classic_metric": r.classic_metric,
            "gen3_metric": r.gen3_metric,
            "status": r.status,
            "attempts": [asdict(a) for a in r.attempts],
        }

    payload = {
        "successful_mappings": [convert(r) for r in passed],
        "failed_mappings": [convert(r) for r in failed],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=180), encoding="utf-8")
    path.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build/validate classic metric -> Grail/Gen3 metric mappings.")
    p.add_argument("--classic-metrics", default=DEFAULT_CURRENT_CLASSIC_METRICS_URL, help="URL or path to current_classic_metrics.json")
    p.add_argument("--mapping-yaml", default=DEFAULT_MAPPING_YAML_URL, help="URL or path to classic_metric_to_grail_metric.yaml")
    p.add_argument("--generate-gen3-dashboards-url", default=DEFAULT_GENERATOR_URL, help="Reference URL for generate_gen3_dashboards.py; kept for traceability")
    p.add_argument("--set-environment-url", default=DEFAULT_SET_ENVIRONMENT_URL, help="URL/path to set_environment.py")
    p.add_argument("--no-remote-set-environment", action="store_true", help="Do not import/call remote set_environment.py")
    p.add_argument("--dt-platform-url", dest="dt_platform_url", default=None, help="https://<tenant>.apps.dynatrace.com or environment URL")
    p.add_argument("--dt-token", dest="dt_token", default=None, help="Dynatrace Platform/OAuth token. Prefer env vars over CLI for security.")
    p.add_argument("--auth-scheme", choices=["auto", "Bearer", "Api-Token"], default="auto")
    p.add_argument("--from", dest="from_expr", default="now() - 30m", help="DQL from expression")
    p.add_argument("--to", dest="to_expr", default="now()", help="DQL to expression")
    p.add_argument("--query-timeout", type=int, default=45)
    p.add_argument("--poll-sleep", type=float, default=1.5)
    p.add_argument("--limit", type=int, default=0, help="Limit number of metrics, useful for shakeout. 0 means all.")
    p.add_argument("--dry-run", action="store_true", help="Create candidate attempts without calling Dynatrace")
    p.add_argument("--output-dir", default=".")
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    classic_data = load_json(args.classic_metrics)
    mapping_data = load_yaml(args.mapping_yaml)
    classic_metrics = flatten_metric_keys(classic_data)
    explicit_mapping = normalize_mapping_yaml(mapping_data)

    if args.limit and args.limit > 0:
        classic_metrics = classic_metrics[: args.limit]

    if not classic_metrics:
        raise SystemExit(f"No metric keys found in classic metrics input using key '{CLASSIC_METRIC_ID_FIELD}'.")

    if args.dry_run:
        base_url, headers = "https://dry-run.apps.dynatrace.com", {}
    else:
        base_url, headers = get_auth_config(args)

    print(f"Loaded {len(classic_metrics)} classic metrics from `{CLASSIC_METRIC_ID_FIELD}`")
    print(f"Loaded {len(explicit_mapping)} explicit mapping entries")
    print(f"DQL endpoint base: {base_url}")
    print(f"Traceability: generate_gen3_dashboards.py = {args.generate_gen3_dashboards_url}")

    passed: List[MetricResult] = []
    failed: List[MetricResult] = []

    for idx, classic_metric in enumerate(classic_metrics, 1):
        candidates = build_candidates(classic_metric, explicit_mapping)
        result = validate_metric(classic_metric, candidates, base_url, headers, args)
        (passed if result.status == "PASSED" else failed).append(result)
        print(f"[{idx}/{len(classic_metrics)}] {result.status}: {classic_metric} -> {result.gen3_metric} ({len(result.attempts)} attempts)")

    write_csv(output_dir / "passed_metric_mapping_report.csv", passed)
    write_csv(output_dir / "failed_metric_mapping_report.csv", failed)
    write_markdown(output_dir / "passed_metric_mapping_report.md", "Passed classic metric to Grail metric mappings", passed)
    write_markdown(output_dir / "failed_metric_mapping_report.md", "Failed classic metric to Grail metric mappings", failed)
    write_verbose_yaml(output_dir / "verbose_classic_metric_to_grail_metric.yaml", passed, failed)

    summary = {
        "classic_metricId_field": CLASSIC_METRIC_ID_FIELD,
        "classic_metrics": len(classic_metrics),
        "passed": len(passed),
        "failed": len(failed),
        "outputs": [
            "passed_metric_mapping_report.csv",
            "passed_metric_mapping_report.md",
            "failed_metric_mapping_report.csv",
            "failed_metric_mapping_report.md",
            "verbose_classic_metric_to_grail_metric.yaml",
            "verbose_classic_metric_to_grail_metric.json",
            "metric_mapping_summary.json",
        ],
    }
    (output_dir / "metric_mapping_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if not failed else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
