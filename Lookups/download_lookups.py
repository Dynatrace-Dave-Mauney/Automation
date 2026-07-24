import csv
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List

import requests


DT_PLATFORM_URL = os.environ["DT_PLATFORM_URL"].rstrip("/")
DT_PLATFORM_TOKEN = os.environ["DT_PLATFORM_TOKEN"]

OUTPUT_DIR = Path("downloads/lookups")

HEADERS = {
    "Authorization": f"Bearer {DT_PLATFORM_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# DQL execution endpoint for Dynatrace Platform Storage query service.
# If this differs in your tenant, verify in:
#   https://<tenant>.apps.dynatrace.com/platform/swagger-ui/index.html
DQL_EXECUTE_URL = f"{DT_PLATFORM_URL}/platform/storage/query/v1/query:execute"
DQL_POLL_URL = f"{DT_PLATFORM_URL}/platform/storage/query/v1/query:poll"


LOOKUP_NAME_PATTERN = re.compile(r"^/lookups/[A-Za-z0-9._/\-]+$")


def validate_lookup_name(name: str) -> None:
    """
    Prevent accidental DQL injection or malformed load paths.
    Grail lookup file names should be under /lookups and use safe path characters.
    """
    if not LOOKUP_NAME_PATTERN.match(name):
        raise ValueError(f"Unexpected lookup name/path: {name!r}")


def dql_string_literal(value: str) -> str:
    """
    DQL load requires a quoted string path.

    Since lookup names are validated first, escaping here is mostly defensive.
    """
    validate_lookup_name(value)
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def local_path_from_grail_name(name: str, default_suffix: str = ".csv") -> Path:
    """
    Convert a Grail lookup name like:

        /lookups/team/app_mapping

    into:

        lookups/team/app_mapping.csv

    If the lookup name already has a file extension, keep it.
    """
    validate_lookup_name(name)

    relative = name.removeprefix("/lookups/").lstrip("/")
    path = OUTPUT_DIR / relative

    if not path.suffix:
        path = path.with_suffix(default_suffix)

    return path


def execute_dql(
    query: str,
    *,
    max_result_records: int = 100_000,
    max_result_bytes: int = 100 * 1024 * 1024,
    poll_interval_seconds: float = 1.0,
    timeout_seconds: int = 300,
) -> Dict[str, Any]:
    """
    Execute arbitrary DQL and return the final JSON response.

    This handles both immediate and async/poll-style responses.

    NOTE:
    Dynatrace response shapes can vary by endpoint/version, so this function
    intentionally supports several common token/status/result field names.
    """
    payload = {
        "query": query,
        "requestTimeoutMilliseconds": 60000,  #  Max allowed, client will wait 300 seconds...
        "maxResultRecords": max_result_records,
        "maxResultBytes": max_result_bytes,
    }

    response = requests.post(
        DQL_EXECUTE_URL,
        headers=HEADERS,
        json=payload,
        timeout=timeout_seconds,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("DQL execute failed")
        print("URL:", response.request.url)
        print("Status:", response.status_code)
        print("Response:", response.text[:2000])
        raise

    data = response.json()

    # Some tenants/endpoints may return completed results immediately.
    if has_records(data):
        return data

    request_token = (
        data.get("requestToken")
        or data.get("request_token")
        or data.get("token")
        or data.get("id")
    )

    if not request_token:
        return data

    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        poll_response = requests.get(
            DQL_POLL_URL,
            headers=HEADERS,
            params={"request-token": request_token},
            timeout=timeout_seconds,
        )

        try:
            poll_response.raise_for_status()
        except requests.HTTPError:
            print("DQL poll failed")
            print("URL:", poll_response.request.url)
            print("Status:", poll_response.status_code)
            print("Response:", poll_response.text[:2000])
            raise

        poll_data = poll_response.json()

        state = (
            poll_data.get("state")
            or poll_data.get("status")
            or poll_data.get("queryStatus")
            or ""
        ).upper()

        if state in {"SUCCEEDED", "SUCCESS", "COMPLETED", "COMPLETE"}:
            return poll_data

        if state in {"FAILED", "CANCELLED", "CANCELED", "ERROR"}:
            raise RuntimeError(f"DQL query failed: {json.dumps(poll_data, indent=2)}")

        if has_records(poll_data):
            return poll_data

        time.sleep(poll_interval_seconds)

    raise TimeoutError(f"DQL query did not complete within {timeout_seconds} seconds")


def has_records(data: Dict[str, Any]) -> bool:
    return bool(extract_records(data))


def extract_records(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Attempt to extract tabular DQL records from several possible response shapes.

    Common shapes may include:
      data["result"]["records"]
      data["result"]["data"]["records"]
      data["records"]
      data["data"]["records"]
    """
    candidates = [
        data.get("records"),
        data.get("data", {}).get("records") if isinstance(data.get("data"), dict) else None,
        data.get("result", {}).get("records") if isinstance(data.get("result"), dict) else None,
        data.get("result", {}).get("data", {}).get("records")
        if isinstance(data.get("result"), dict)
        and isinstance(data.get("result", {}).get("data"), dict)
        else None,
    ]

    for candidate in candidates:
        if isinstance(candidate, list):
            return candidate

    return []


def list_lookup_names() -> List:
    """
    List Grail lookup files using dt.system.files.

    You may need to adjust field names after inspecting your tenant's output.
    """
    query = """
fetch dt.system.files
| filter startsWith(name, "/lookups/")
| fields name
| sort name asc
"""

    data = execute_dql(query)
    records = extract_records(data)

    lookup_names = []

    for record in records:
        name = record.get("name") or record.get("path")

        if not name:
            print(f"Skipping record without name/path: {record}")
            continue

        validate_lookup_name(name)
        lookup_names.append(name)

    return lookup_names


def normalize_value(value: Any) -> Any:
    """
    CSV-friendly value conversion.
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def write_records_to_csv(records: List[Dict[str, Any]], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        output_file.write_text("", encoding="utf-8")
        return

    fieldnames = sorted({key for record in records for key in record.keys()})

    with output_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            writer.writerow({
                key: normalize_value(record.get(key))
                for key in fieldnames
            })


def download_lookup_via_load(name: str) -> Path:
    """
    Runs:

        load "/lookups/..."

    and writes the result records to a local CSV file.
    """
    validate_lookup_name(name)

    query = f"""
load {dql_string_literal(name)}
"""

    data = execute_dql(query)
    records = extract_records(data)

    output_file = local_path_from_grail_name(name)
    write_records_to_csv(records, output_file)

    return output_file


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lookup_names = list_lookup_names()

    print(f"Found {len(lookup_names)} lookup file(s)")

    for name in lookup_names:
        print(f"Loading {name}")

        try:
            output_file = download_lookup_via_load(name)
            print(f"Saved {name} -> {output_file}")
        except Exception as e:
            print(f"Failed to save {name}: {e}")


if __name__ == "__main__":
    main()
