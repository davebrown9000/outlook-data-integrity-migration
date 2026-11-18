"""Offline mailbox migration planning and reconciliation using fictional records.

No Microsoft Graph integration, credentials, external calls, or mailbox mutations.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


class MigrationError(ValueError):
    """An unsafe or inconsistent migration plan."""


def _unique_index(records: list[dict[str, Any]], field: str, kind: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            raise MigrationError(f"{kind} requires nonempty {field}")
        if value in result:
            raise MigrationError(f"duplicate {kind} {field}: {value}")
        result[value] = dict(record)
    return result


def plan_migration(messages: list[dict[str, Any]], folders: list[dict[str, Any]],
                   decisions: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Validate all proposed moves before returning a deterministic, read-only plan.

    Identifier here is a fictional stable identifier, not a Graph message ID.
    """
    by_id = _unique_index(messages, "stable_id", "message")
    by_folder = _unique_index(folders, "folder", "folder")
    by_decision = _unique_index(decisions, "stable_id", "decision")
    results: list[dict[str, str]] = []
    for stable_id, decision in sorted(by_decision.items()):
        if stable_id not in by_id:
            raise MigrationError(f"source message missing: {stable_id}")
        message = by_id[stable_id]
        source = message.get("folder")
        target = decision.get("destination")
        if source not in by_folder:
            raise MigrationError(f"source folder missing: {source}")
        if not isinstance(target, str) or target not in by_folder:
            raise MigrationError(f"destination folder missing: {target}")
        if decision.get("expected_source") != source:
            raise MigrationError(f"source changed since preview: {stable_id}")
        if source == target:
            action = "unchanged"
        else:
            action = "move"
        results.append({"stable_id": stable_id, "source": source,
                        "destination": target, "action": action})
    return results


def simulate_plan(messages: list[dict[str, Any]], plan: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Pure simulation; never modifies inputs or an external system."""
    by_id = _unique_index(messages, "stable_id", "message")
    seen: set[str] = set()
    updated = {key: dict(value) for key, value in by_id.items()}
    for item in plan:
        stable_id = item.get("stable_id")
        if stable_id in seen or stable_id not in updated:
            raise MigrationError(f"duplicate or missing plan ID: {stable_id}")
        seen.add(stable_id)
        if updated[stable_id].get("folder") != item.get("source"):
            raise MigrationError(f"stale plan source: {stable_id}")
        if item.get("action") not in ("move", "unchanged"):
            raise MigrationError(f"unrecognised action: {stable_id}")
        if item["action"] == "unchanged" and item["destination"] != item["source"]:
            raise MigrationError(f"invalid unchanged action: {stable_id}")
        if item["action"] == "move" and item["destination"] == item["source"]:
            raise MigrationError(f"invalid move action: {stable_id}")
        updated[stable_id]["folder"] = item["destination"]
    return [updated[key] for key in sorted(updated)]


def reconcile(before: list[dict[str, Any]], after: list[dict[str, Any]],
              plan: list[dict[str, str]]) -> dict[str, Any]:
    """Check stable-ID preservation, message totals and planned destinations."""
    a = _unique_index(before, "stable_id", "before-message")
    b = _unique_index(after, "stable_id", "after-message")
    if set(a) != set(b):
        raise MigrationError("identity reconciliation failed: missing or additional IDs")
    planned = _unique_index(plan, "stable_id", "plan")
    moved = 0
    for stable_id, original in a.items():
        target = planned[stable_id]["destination"] if stable_id in planned else original.get("folder")
        if b[stable_id].get("folder") != target:
            raise MigrationError(f"destination reconciliation failed: {stable_id}")
        if stable_id in planned and planned[stable_id]["action"] == "move":
            moved += 1
    counts_before = dict(sorted(Counter(row.get("folder") for row in before).items()))
    counts_after = dict(sorted(Counter(row.get("folder") for row in after).items()))
    return {"identities_preserved": True, "before_count": len(a),
            "after_count": len(b), "planned_moves": moved,
            "folder_counts_before": counts_before, "folder_counts_after": counts_after}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/fictional_mailbox.json")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    plan = plan_migration(payload["messages"], payload["folders"], payload["decisions"])
    after = simulate_plan(payload["messages"], plan)
    print(json.dumps({"dry_run": True, "plan": plan,
                      "reconciliation": reconcile(payload["messages"], after, plan)}, indent=2))


if __name__ == "__main__":
    main()
