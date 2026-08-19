#!/usr/bin/env python3
"""Audit a saved lark-cli Base record-list response and plan duplicate cleanup without deleting anything."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def field_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list) and len(value) == 1:
        return field_text(value[0])
    if isinstance(value, dict):
        for key in ("text", "value", "name"):
            if key in value:
                return field_text(value[key])
    return str(value).strip()


def parse_record_list(payload: Any) -> tuple[list[dict[str, Any]], bool, int | None, str]:
    if not isinstance(payload, dict):
        raise ValueError("record-list JSON must be an object")
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        raise ValueError("record-list data must be an object")

    has_more = bool(data.get("has_more", False))
    total = data.get("total")
    total = int(total) if isinstance(total, (int, float)) else None

    for list_key in ("items", "records"):
        items = data.get(list_key)
        if isinstance(items, list):
            records = []
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    raise ValueError(f"{list_key}[{index}] is not an object")
                fields = item.get("fields") or item.get("field_values") or item.get("values") or {}
                if not isinstance(fields, dict):
                    raise ValueError(f"{list_key}[{index}] fields are not an object")
                records.append({"record_id": field_text(item.get("record_id") or item.get("id")), "fields": fields})
            return records, has_more, total, f"object-list:{list_key}"

    matrix = data.get("data")
    fields = data.get("fields")
    record_ids = data.get("record_id_list")
    if isinstance(matrix, list) and isinstance(fields, list) and isinstance(record_ids, list):
        if len(matrix) != len(record_ids):
            raise ValueError(f"matrix row count {len(matrix)} does not match record_id_list count {len(record_ids)}")
        if len(set(map(str, fields))) != len(fields):
            raise ValueError("matrix fields contain duplicate names")
        records = []
        for index, row in enumerate(matrix):
            if not isinstance(row, list) or len(row) != len(fields):
                raise ValueError(f"matrix row {index} width does not match fields")
            records.append({
                "record_id": field_text(record_ids[index]),
                "fields": {str(name): row[column] for column, name in enumerate(fields)},
            })
        return records, has_more, total, "matrix"

    raise ValueError("unsupported record-list shape; expected data.items/data.records or data.data+data.fields+data.record_id_list")


def expected_ids_from_normalized(path: Path) -> list[str]:
    payload = load_json(path)
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError("expected normalized JSON must contain records[]")
    ids = [field_text(record.get("source_record_id")) for record in records if isinstance(record, dict)]
    if len(ids) != len(records):
        raise ValueError("normalized records contain a non-object item")
    blanks = [index + 1 for index, value in enumerate(ids) if not value]
    duplicates = sorted(key for key, count in Counter(ids).items() if key and count > 1)
    if blanks or duplicates:
        raise ValueError(f"normalized key set is invalid: blanks={blanks}, duplicates={duplicates}")
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record_list", type=Path, help="Saved JSON output from lark-cli base +record-list")
    parser.add_argument("--expected-normalized", type=Path, help="Reviewed normalized.json containing records[].source_record_id")
    parser.add_argument("--expected-count", type=int, help="Expected unique count when normalized JSON is unavailable")
    parser.add_argument("--key-field", default="源记录ID")
    parser.add_argument("--action-field", default="行动")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cleanup-plan", type=Path, help="Write an exact read-only duplicate cleanup plan when safe")
    args = parser.parse_args()

    if args.cleanup_plan and not args.expected_normalized:
        parser.error("--cleanup-plan requires --expected-normalized so the exact expected key set can be verified")

    try:
        records, has_more, total, response_shape = parse_record_list(load_json(args.record_list))
        expected_ids = expected_ids_from_normalized(args.expected_normalized) if args.expected_normalized else None
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit failed: {exc}", file=sys.stderr)
        return 2

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    blank_key_records: list[str] = []
    blank_record_id_indexes: list[int] = []
    for index, record in enumerate(records):
        record_id = field_text(record.get("record_id"))
        if not record_id:
            blank_record_id_indexes.append(index)
        key = field_text(record["fields"].get(args.key_field))
        if not key:
            blank_key_records.append(record_id or f"index:{index}")
            continue
        groups[key].append({
            "record_id": record_id,
            "source_record_id": key,
            "action": field_text(record["fields"].get(args.action_field)),
        })

    record_id_counts = Counter(field_text(record.get("record_id")) for record in records)
    duplicate_record_ids = sorted(key for key, count in record_id_counts.items() if key and count > 1)
    actual_keys = set(groups)
    expected_set = set(expected_ids or [])
    missing_expected = sorted(expected_set - actual_keys) if expected_ids is not None else []
    unexpected = sorted(actual_keys - expected_set) if expected_ids is not None else []
    duplicate_keys = {key: len(group) for key, group in groups.items() if len(group) > 1}
    expected_count = len(expected_ids) if expected_ids is not None else args.expected_count
    total_matches_payload = total is None or total == len(records)
    count_matches = expected_count is None or len(actual_keys) == expected_count

    safe_key_set = (
        not has_more
        and not blank_key_records
        and not blank_record_id_indexes
        and not duplicate_record_ids
        and total_matches_payload
        and count_matches
        and not missing_expected
        and not unexpected
    )
    audit = {
        "schema_version": 1,
        "record_list_file": str(args.record_list),
        "response_shape": response_shape,
        "has_more": has_more,
        "payload_total": total,
        "actual_record_count": len(records),
        "unique_source_record_count": len(actual_keys),
        "expected_unique_count": expected_count,
        "total_matches_payload": total_matches_payload,
        "key_set_matches_expected": safe_key_set,
        "blank_key_record_ids": blank_key_records,
        "blank_record_id_indexes": blank_record_id_indexes,
        "duplicate_record_ids": duplicate_record_ids,
        "duplicate_source_record_ids": duplicate_keys,
        "missing_expected_source_record_ids": missing_expected,
        "unexpected_source_record_ids": unexpected,
        "cleanup_plan_written": False,
        "deletes_records": False,
    }

    if args.cleanup_plan and duplicate_keys and safe_key_set:
        keep: list[dict[str, str]] = []
        delete: list[dict[str, str]] = []
        for key in sorted(groups):
            keep.append(groups[key][0])
            delete.extend(groups[key][1:])
        cleanup = {
            "schema_version": 1,
            "record_list_file": str(args.record_list),
            "selection_policy": "keep_first_returned_record_for_each_source_record_id",
            "expected_unique_count": len(expected_ids or []),
            "keep_count": len(keep),
            "delete_count": len(delete),
            "keep": keep,
            "delete": delete,
            "requires_explicit_user_authorization": True,
            "deletion_recoverable": False,
        }
        args.cleanup_plan.parent.mkdir(parents=True, exist_ok=True)
        args.cleanup_plan.write_text(json.dumps(cleanup, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        audit["cleanup_plan_written"] = True
        audit["cleanup_plan_file"] = str(args.cleanup_plan)
        audit["planned_delete_count"] = len(delete)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False))

    if has_more or not safe_key_set:
        return 4
    if duplicate_keys:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
