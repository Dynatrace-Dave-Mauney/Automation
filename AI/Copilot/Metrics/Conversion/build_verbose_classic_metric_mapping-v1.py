#!/usr/bin/env python3
"""
build_verbose_classic_metric_mapping.py

Build a verbose mapping from currently written Classic metric keys to likely/current
Grail/Gen3 metric keys.

Inputs, by default, are resolved relative to this module first and then relative to
common repository locations under AI/Copilot:
  - current_classic_metrics.json
      Output from Metrics API v2 GET /metrics using writtenSince, or any JSON
      shape containing metric keys.
  - fetch_metric_series.csv
      CSV exported from DQL such as: fetch metric.series
      The module extracts Gen3 metric names from likely columns such as
      metric.key, metric, metricName, name, timeseries, or from a one-column CSV.
  - optional seed mapping files, if present:
      classic_metric_mapping.json, classic_to_grail_metric_mapping.json,
      verbose_classic_metric_mapping.json, classic_metric_mapping.csv

Major behaviors added:
  - current_classic_metrics.json is the primary driver for classic metrics.
  - Classic dsfm: metrics are converted to dt.sfm.* candidates.
  - fetch_metric_series.csv is used as the current Gen3 metric universe and to
    discover pattern matches that improve mapping coverage.
  - Produces verbose JSON and CSV outputs including match method, score,
    candidate list, and notes.

This script is intentionally conservative: it will mark weak/fuzzy mappings as
low-confidence instead of pretending they are exact.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


DEFAULT_CLASSIC_JSON = "current_classic_metrics.json"
DEFAULT_GEN3_CSV = "fetch_metric_series.csv"
DEFAULT_OUTPUT_JSON = "verbose_classic_metric_mapping.json"
DEFAULT_OUTPUT_CSV = "verbose_classic_metric_mapping.csv"

COMMON_SEED_MAPPING_FILES = (
    "classic_metric_mapping.json",
    "classic_to_grail_metric_mapping.json",
    "classic_to_gen3_metric_mapping.json",
    "metric_mapping.json",
    "verbose_classic_metric_mapping.json",
    "classic_metric_mapping.csv",
)

# Prefix conversions known or useful during Classic -> Grail/Gen3 migration.
# The dsfm rule is specifically requested: dsfm:foo.bar -> dt.sfm.foo.bar
PREFIX_CONVERSIONS = {
    "dsfm:": "dt.sfm.",
}

# Metric-ish token detector. It knowingly accepts both Classic and Grail shapes.
METRIC_KEY_RE = re.compile(
    r"(?:builtin:|ext:|calc:|custom:|dsfm:|dt\.|cloud\.|func:|log\.|span\.)"
    r"[A-Za-z0-9_.:/\-]+"
)


@dataclass(order=True)
class CandidateMatch:
    sort_index: Tuple[int, str] = field(init=False, repr=False)
    score: int
    gen3_metric: str
    method: str
    reason: str

    def __post_init__(self) -> None:
        # Desc sort by score, then stable name sort.
        self.sort_index = (-self.score, self.gen3_metric)


@dataclass
class MappingRecord:
    classic_metric: str
    mapped_metric: Optional[str]
    confidence: str
    score: int
    method: str
    reason: str
    candidates: List[CandidateMatch]
    notes: List[str] = field(default_factory=list)

    def to_jsonable(self) -> Dict[str, Any]:
        data = asdict(self)
        data["candidates"] = [asdict(c) | {"sort_index": None} for c in self.candidates]
        for c in data["candidates"]:
            c.pop("sort_index", None)
        return data


def resolve_path(path_value: str | Path, search_roots: Sequence[Path]) -> Path:
    """Resolve a file path against cwd, script dir, and known repo-ish roots."""
    p = Path(path_value).expanduser()
    if p.is_absolute() and p.exists():
        return p
    if p.exists():
        return p.resolve()
    for root in search_roots:
        candidate = root / p
        if candidate.exists():
            return candidate.resolve()
    # Return the cwd-relative path when not found so error messages are clear.
    return p.resolve()


def default_search_roots() -> List[Path]:
    here = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    roots = [cwd, here]
    # Include common paths when run from repo root or from AI/Copilot subdirs.
    for base in [cwd, here, *here.parents, *cwd.parents]:
        roots.extend([
            base / "AI" / "Copilot",
            base / "AI" / "Copilot" / "Dashboards" / "Generation",
            base / "NewPlatform" / "Dashboards",
        ])
    # De-dupe while preserving order.
    seen: Set[Path] = set()
    out: List[Path] = []
    for r in roots:
        try:
            rr = r.resolve()
        except OSError:
            rr = r
        if rr not in seen:
            seen.add(rr)
            out.append(rr)
    return out


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_metric_keys_from_any_json(obj: Any) -> List[str]:
    """Extract unique metric keys from flexible JSON shapes.

    Supports Metrics API v2 shapes like {"metrics": [{"metricId": "..."}]},
    simpler lists of strings, dicts with keys/id/name/metricId, and nested data.
    """
    found: List[str] = []

    def add(value: Any) -> None:
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return
            # Prefer the whole string if it looks like a metric key; otherwise scan.
            if METRIC_KEY_RE.fullmatch(s) or ":" in s or "." in s:
                if not s.lower().startswith(("http://", "https://")):
                    found.append(s)
            for m in METRIC_KEY_RE.findall(s):
                found.append(m)

    def walk(value: Any) -> None:
        if isinstance(value, str):
            add(value)
        elif isinstance(value, Mapping):
            # Metrics API v2 commonly uses metricId.
            for k in ("metricId", "metricKey", "key", "id", "name", "metric", "metricName"):
                if k in value:
                    add(value[k])
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(obj)
    return sorted(dedupe(found))


def load_current_classic_metrics(path: Path) -> List[str]:
    data = load_json(path)
    metrics = extract_metric_keys_from_any_json(data)
    if not metrics:
        raise ValueError(f"No metric keys found in {path}")
    return metrics


def dedupe(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for v in values:
        s = str(v).strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def extract_metric_from_csv_row(row: Mapping[str, str]) -> List[str]:
    preferred_columns = [
        "metric.key", "metric_key", "metric", "metric.name", "metricName",
        "metric_name", "name", "timeseries", "series", "key", "id",
    ]
    values: List[str] = []
    lowered = {k.lower(): k for k in row.keys()}
    for preferred in preferred_columns:
        actual = lowered.get(preferred.lower())
        if actual and row.get(actual):
            values.append(str(row[actual]).strip())
    if not values:
        for value in row.values():
            if value:
                values.extend(METRIC_KEY_RE.findall(str(value)))
    return values


def sniff_csv_dialect(sample: str) -> csv.Dialect:
    """Sniff CSV dialect without mistaking metric dots for delimiters."""
    # Dynatrace metric names are dot-heavy, so csv.Sniffer can incorrectly
    # choose '.' as a delimiter. Prefer common export delimiters explicitly.
    first_line = sample.splitlines()[0] if sample.splitlines() else sample
    if "," in first_line:
        return csv.excel
    if "\t" in first_line:
        class TabDialect(csv.excel):
            delimiter = "\t"
        return TabDialect
    if ";" in first_line:
        class SemicolonDialect(csv.excel):
            delimiter = ";"
        return SemicolonDialect
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect
    except csv.Error:
        return csv.excel


def load_gen3_metrics_from_csv(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        if not sample.strip():
            return []
        dialect = sniff_csv_dialect(sample)
        try:
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            has_header = True

        metrics: List[str] = []
        if has_header:
            reader = csv.DictReader(f, dialect=dialect)
            for row in reader:
                metrics.extend(extract_metric_from_csv_row(row))
        else:
            reader = csv.reader(f, dialect=dialect)
            for row in reader:
                if not row:
                    continue
                if len(row) == 1:
                    metrics.append(row[0].strip())
                else:
                    for cell in row:
                        metrics.extend(METRIC_KEY_RE.findall(cell))
    return sorted(dedupe(m for m in metrics if looks_like_metric_key(m)))


def looks_like_metric_key(value: str) -> bool:
    s = value.strip()
    if not s or " " in s or s.startswith("{") or s.startswith("["):
        return False
    return bool(METRIC_KEY_RE.match(s)) or s.startswith("dt.")


def normalize_for_match(metric: str) -> str:
    s = metric.lower().strip()
    for old, new in PREFIX_CONVERSIONS.items():
        if s.startswith(old):
            s = new + s[len(old):]
    s = re.sub(r"^(builtin:|ext:|calc:|custom:)", "", s)
    s = s.replace(":", ".")
    s = re.sub(r"[^a-z0-9]+", ".", s)
    s = re.sub(r"\.+", ".", s).strip(".")
    return s


def token_set(metric: str) -> Set[str]:
    normalized = normalize_for_match(metric)
    return {t for t in normalized.split(".") if t and not t.isdigit()}


def dsfm_to_dt_sfm(metric: str) -> Optional[str]:
    if metric.startswith("dsfm:"):
        return "dt.sfm." + metric[len("dsfm:"):].lstrip(".:")
    return None


def generate_deterministic_candidates(classic_metric: str) -> List[Tuple[str, str]]:
    """Create deterministic candidates before fuzzy lookup."""
    candidates: List[Tuple[str, str]] = []
    dsfm_candidate = dsfm_to_dt_sfm(classic_metric)
    if dsfm_candidate:
        candidates.append((dsfm_candidate, "dsfm_prefix_conversion"))

    normalized = normalize_for_match(classic_metric)
    candidates.append((normalized, "normalized_key"))

    # Common Classic shape: builtin:tech.metric -> tech.metric; Gen3 may be dt.tech.metric.
    if classic_metric.startswith("builtin:"):
        rest = classic_metric[len("builtin:"):]
        candidates.extend([
            (rest, "builtin_prefix_removed"),
            ("dt." + rest, "builtin_to_dt_prefix_candidate"),
        ])
    return dedupe_candidate_pairs(candidates)


def dedupe_candidate_pairs(pairs: Iterable[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen: Set[str] = set()
    out: List[Tuple[str, str]] = []
    for candidate, method in pairs:
        c = candidate.strip()
        if c and c not in seen:
            seen.add(c)
            out.append((c, method))
    return out


def score_candidate(classic_metric: str, gen3_metric: str, method_hint: str = "pattern") -> Optional[CandidateMatch]:
    c_norm = normalize_for_match(classic_metric)
    g_norm = normalize_for_match(gen3_metric)
    c_tokens = token_set(classic_metric)
    g_tokens = token_set(gen3_metric)

    if not c_norm or not g_norm:
        return None

    # Exact and deterministic rules.
    if classic_metric == gen3_metric:
        return CandidateMatch(100, gen3_metric, "exact", "Classic metric key exactly exists in current Gen3 metric series")

    converted = dsfm_to_dt_sfm(classic_metric)
    if converted and converted == gen3_metric:
        return CandidateMatch(98, gen3_metric, "dsfm_prefix_conversion_exact", "Converted dsfm: prefix to dt.sfm. and found exact current Gen3 metric")

    for deterministic, method in generate_deterministic_candidates(classic_metric):
        d_norm = normalize_for_match(deterministic)
        if d_norm == g_norm:
            score = 97 if method == "dsfm_prefix_conversion" else 92
            reason = f"Deterministic candidate {deterministic!r} matched current Gen3 metric after normalization"
            return CandidateMatch(score, gen3_metric, method, reason)

    # Pattern match: suffix/prefix containment after removing prefixes.
    if c_norm.endswith(g_norm) or g_norm.endswith(c_norm):
        return CandidateMatch(86, gen3_metric, "suffix_or_prefix", "Normalized Classic and Gen3 keys have suffix/prefix containment")

    if c_norm in g_norm or g_norm in c_norm:
        return CandidateMatch(78, gen3_metric, "contains", "Normalized Classic and Gen3 keys contain each other")

    # Token overlap/fuzzy similarity. Keep conservative thresholds.
    if c_tokens and g_tokens:
        intersection = c_tokens & g_tokens
        union = c_tokens | g_tokens
        jaccard = len(intersection) / len(union)
        sequence = SequenceMatcher(None, c_norm, g_norm).ratio()
        score = int(round(max(jaccard * 100, sequence * 100)))
        if len(intersection) >= 2 and score >= 64:
            return CandidateMatch(
                score,
                gen3_metric,
                method_hint,
                f"Pattern match from fetch_metric_series.csv; shared tokens: {', '.join(sorted(intersection))}",
            )
        if score >= 82:
            return CandidateMatch(score, gen3_metric, "fuzzy", "High normalized string similarity")
    return None


def build_seed_mapping(paths: Sequence[Path]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for path in paths:
        if not path.exists():
            continue
        try:
            if path.suffix.lower() == ".json":
                data = load_json(path)
                mapping.update(extract_mapping_from_json(data))
            elif path.suffix.lower() == ".csv":
                mapping.update(extract_mapping_from_csv(path))
        except Exception as e:
            print(f"WARNING: could not read seed mapping {path}: {e}", file=sys.stderr)
    return mapping


def extract_mapping_from_json(data: Any) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if isinstance(data, Mapping):
        # Simple {classic: gen3} shape.
        for k, v in data.items():
            if isinstance(v, str) and looks_like_metric_key(k) and looks_like_metric_key(v):
                out[str(k)] = str(v)
            elif isinstance(v, Mapping):
                classic = v.get("classic_metric") or v.get("classic") or v.get("source") or k
                gen3 = v.get("mapped_metric") or v.get("gen3_metric") or v.get("grail_metric") or v.get("target")
                if isinstance(classic, str) and isinstance(gen3, str):
                    out[classic] = gen3
        # Also scan nested lists under common keys.
        for key in ("mappings", "records", "metrics"):
            if key in data:
                out.update(extract_mapping_from_json(data[key]))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, Mapping):
                classic = item.get("classic_metric") or item.get("classic") or item.get("source") or item.get("from")
                gen3 = item.get("mapped_metric") or item.get("gen3_metric") or item.get("grail_metric") or item.get("target") or item.get("to")
                if isinstance(classic, str) and isinstance(gen3, str):
                    out[classic] = gen3
    return out


def extract_mapping_from_csv(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = sniff_csv_dialect(sample)
        reader = csv.DictReader(f, dialect=dialect)
        if not reader.fieldnames:
            return out
        lower = {c.lower(): c for c in reader.fieldnames}
        classic_col = lower.get("classic_metric") or lower.get("classic") or lower.get("source") or lower.get("from")
        gen3_col = lower.get("mapped_metric") or lower.get("gen3_metric") or lower.get("grail_metric") or lower.get("target") or lower.get("to")
        if not classic_col or not gen3_col:
            return out
        for row in reader:
            classic = (row.get(classic_col) or "").strip()
            gen3 = (row.get(gen3_col) or "").strip()
            if classic and gen3:
                out[classic] = gen3
    return out


def confidence_for_score(score: int, method: str) -> str:
    if score >= 95 or method in {"exact", "dsfm_prefix_conversion_exact"}:
        return "high"
    if score >= 82:
        return "medium"
    if score >= 64:
        return "low"
    return "none"


def map_metric(classic_metric: str, gen3_metrics: Sequence[str], gen3_index: Set[str], seed_mapping: Mapping[str, str], max_candidates: int) -> MappingRecord:
    notes: List[str] = []

    # Existing/seed mapping wins only if the target exists in the current Gen3 universe.
    seed_target = seed_mapping.get(classic_metric)
    if seed_target:
        if seed_target in gen3_index:
            c = CandidateMatch(99, seed_target, "seed_mapping_current", "Seed mapping target exists in fetch_metric_series.csv")
            return MappingRecord(classic_metric, seed_target, "high", c.score, c.method, c.reason, [c], notes)
        notes.append(f"Seed mapping target {seed_target!r} was not found in fetch_metric_series.csv; falling back to pattern matching")

    matches: List[CandidateMatch] = []

    # Fast deterministic lookups.
    deterministic_pairs = generate_deterministic_candidates(classic_metric)
    deterministic_values = {candidate: method for candidate, method in deterministic_pairs}
    for candidate, method in deterministic_pairs:
        if candidate in gen3_index:
            reason = f"Deterministic candidate {candidate!r} exists in fetch_metric_series.csv"
            score = 98 if method == "dsfm_prefix_conversion" else 94
            matches.append(CandidateMatch(score, candidate, method + "_current", reason))

    # Exact current key.
    if classic_metric in gen3_index:
        matches.append(CandidateMatch(100, classic_metric, "exact_current", "Classic metric key exists in fetch_metric_series.csv"))

    # Pattern/fuzzy search against current Gen3 universe.
    # Limit cost on very large tenants by prefiltering on shared token presence.
    c_tokens = token_set(classic_metric)
    c_norm = normalize_for_match(classic_metric)
    for gen3 in gen3_metrics:
        if gen3 in deterministic_values or gen3 == classic_metric:
            continue
        g_norm = normalize_for_match(gen3)
        g_tokens = token_set(gen3)
        should_score = False
        if c_norm and (c_norm in g_norm or g_norm in c_norm):
            should_score = True
        elif c_tokens and len(c_tokens & g_tokens) >= 2:
            should_score = True
        elif classic_metric.startswith("dsfm:") and gen3.startswith("dt.sfm."):
            should_score = bool(c_tokens & g_tokens)
        if not should_score:
            continue
        match = score_candidate(classic_metric, gen3)
        if match:
            matches.append(match)

    # Remove duplicate gen3 keys, keeping highest score.
    best_by_metric: Dict[str, CandidateMatch] = {}
    for m in matches:
        prev = best_by_metric.get(m.gen3_metric)
        if prev is None or m.score > prev.score:
            best_by_metric[m.gen3_metric] = m
    candidates = sorted(best_by_metric.values())[:max_candidates]

    if not candidates:
        converted = dsfm_to_dt_sfm(classic_metric)
        if converted:
            notes.append(f"Applied dsfm conversion candidate {converted!r}, but it was not present in fetch_metric_series.csv")
        return MappingRecord(classic_metric, None, "none", 0, "unmapped", "No current Gen3 candidate found", [], notes)

    best = candidates[0]
    confidence = confidence_for_score(best.score, best.method)
    mapped = best.gen3_metric if confidence in {"high", "medium"} else None
    if confidence == "low":
        notes.append("Low-confidence candidate retained for review but not selected as mapped_metric")
    return MappingRecord(classic_metric, mapped, confidence, best.score, best.method, best.reason, candidates, notes)


def write_json(path: Path, records: Sequence[MappingRecord], meta: Mapping[str, Any]) -> None:
    payload = {
        "metadata": dict(meta),
        "mappings": [record.to_jsonable() for record in records],
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=False)
        f.write("\n")


def write_csv(path: Path, records: Sequence[MappingRecord]) -> None:
    fieldnames = [
        "classic_metric", "mapped_metric", "confidence", "score", "method",
        "reason", "candidate_count", "candidates", "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "classic_metric": r.classic_metric,
                "mapped_metric": r.mapped_metric or "",
                "confidence": r.confidence,
                "score": r.score,
                "method": r.method,
                "reason": r.reason,
                "candidate_count": len(r.candidates),
                "candidates": json.dumps([asdict(c) | {"sort_index": None} for c in r.candidates], ensure_ascii=False),
                "notes": " | ".join(r.notes),
            })


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build verbose current Classic -> Gen3 metric mapping")
    parser.add_argument("--classic-json", default=DEFAULT_CLASSIC_JSON, help="Path to current_classic_metrics.json")
    parser.add_argument("--gen3-csv", default=DEFAULT_GEN3_CSV, help="Path to fetch_metric_series.csv")
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON, help="Output verbose JSON path")
    parser.add_argument("--output-csv", default=DEFAULT_OUTPUT_CSV, help="Output verbose CSV path")
    parser.add_argument("--seed-mapping", action="append", default=[], help="Optional seed mapping JSON/CSV. Can be specified multiple times.")
    parser.add_argument("--max-candidates", type=int, default=5, help="Max candidate matches to retain per classic metric")
    parser.add_argument("--fail-on-missing-gen3-csv", action="store_true", help="Fail if fetch_metric_series.csv is missing instead of producing unmapped records")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    roots = default_search_roots()

    classic_path = resolve_path(args.classic_json, roots)
    gen3_path = resolve_path(args.gen3_csv, roots)
    output_json = Path(args.output_json).expanduser().resolve()
    output_csv = Path(args.output_csv).expanduser().resolve()

    if not classic_path.exists():
        print(f"ERROR: classic metrics JSON not found: {classic_path}", file=sys.stderr)
        return 2

    classic_metrics = load_current_classic_metrics(classic_path)

    if gen3_path.exists():
        gen3_metrics = load_gen3_metrics_from_csv(gen3_path)
    elif args.fail_on_missing_gen3_csv:
        print(f"ERROR: Gen3 metric CSV not found: {gen3_path}", file=sys.stderr)
        return 2
    else:
        print(f"WARNING: Gen3 metric CSV not found: {gen3_path}; only deterministic/non-current checks are possible", file=sys.stderr)
        gen3_metrics = []

    # Resolve optional seed mappings plus common files in the same dirs.
    seed_paths: List[Path] = []
    for seed in args.seed_mapping:
        seed_paths.append(resolve_path(seed, roots))
    for root in roots:
        for name in COMMON_SEED_MAPPING_FILES:
            p = root / name
            if p.exists() and p.resolve() not in {sp.resolve() for sp in seed_paths if sp.exists()}:
                seed_paths.append(p.resolve())

    seed_mapping = build_seed_mapping(seed_paths)
    gen3_index = set(gen3_metrics)

    records = [
        map_metric(metric, gen3_metrics, gen3_index, seed_mapping, args.max_candidates)
        for metric in classic_metrics
    ]

    mapped_count = sum(1 for r in records if r.mapped_metric)
    high_count = sum(1 for r in records if r.confidence == "high")
    medium_count = sum(1 for r in records if r.confidence == "medium")
    low_count = sum(1 for r in records if r.confidence == "low")
    unmapped_count = sum(1 for r in records if r.confidence == "none")
    dsfm_count = sum(1 for r in records if r.classic_metric.startswith("dsfm:"))
    dsfm_mapped_count = sum(1 for r in records if r.classic_metric.startswith("dsfm:") and r.mapped_metric)

    meta = {
        "classic_metrics_source": str(classic_path),
        "gen3_metrics_source": str(gen3_path) if gen3_path.exists() else None,
        "seed_mapping_sources": [str(p) for p in seed_paths if p.exists()],
        "classic_metric_count": len(classic_metrics),
        "gen3_metric_count": len(gen3_metrics),
        "mapped_count": mapped_count,
        "high_confidence_count": high_count,
        "medium_confidence_count": medium_count,
        "low_confidence_candidate_only_count": low_count,
        "unmapped_count": unmapped_count,
        "dsfm_classic_count": dsfm_count,
        "dsfm_mapped_count": dsfm_mapped_count,
        "prefix_conversions": PREFIX_CONVERSIONS,
    }

    write_json(output_json, records, meta)
    write_csv(output_csv, records)

    print(json.dumps(meta, indent=2))
    print(f"Wrote {output_json}")
    print(f"Wrote {output_csv}")
    return 0 if mapped_count or not gen3_metrics else 1


if __name__ == "__main__":
    raise SystemExit(main())
