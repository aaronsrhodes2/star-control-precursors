"""Audit asset placeholder status — see references/project-rules.md
Rule 1. Reads assets/_PLACEHOLDERS.json and prints how many entries
are still placeholders vs improved/replaced, per category.

Usage:
    .venv/Scripts/python.exe tools/audit_placeholders.py
    .venv/Scripts/python.exe tools/audit_placeholders.py --category ships
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "assets" / "_PLACEHOLDERS.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="filter to one category")
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="list every non-placeholder entry with its status",
    )
    args = parser.parse_args()

    if not MANIFEST.exists():
        print(f"no manifest at {MANIFEST}; run extract_uqm_graphical_assets.py first",
              file=sys.stderr)
        return 1
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.category:
        data = {k: v for k, v in data.items() if v["category"] == args.category}

    by_cat_status: dict[str, dict[str, int]] = {}
    for k, v in data.items():
        cat = v["category"]
        st = v["status"]
        by_cat_status.setdefault(cat, {}).setdefault(st, 0)
        by_cat_status[cat][st] += 1

    total = len(data)
    total_placeholder = sum(1 for v in data.values() if v["status"] == "placeholder")
    total_improved = sum(1 for v in data.values() if v["status"] == "improved")
    total_replaced = sum(1 for v in data.values() if v["status"] == "replaced")

    print(f"Asset manifest — {total} tracked files")
    print(f"  placeholder: {total_placeholder}")
    print(f"  improved:    {total_improved}")
    print(f"  replaced:    {total_replaced}")
    pct_done = (
        100.0 * (total_improved + total_replaced) / total if total else 0.0
    )
    print(f"  progress:    {pct_done:.1f}% non-placeholder")

    print("\nBy category:")
    print(f"  {'category':12s} {'placeholder':>12} {'improved':>10} {'replaced':>10}")
    for cat in sorted(by_cat_status.keys()):
        st = by_cat_status[cat]
        print(
            f"  {cat:12s} {st.get('placeholder', 0):>12} "
            f"{st.get('improved', 0):>10} {st.get('replaced', 0):>10}"
        )

    if args.verbose:
        print("\nNon-placeholder entries:")
        for k, v in sorted(data.items()):
            if v["status"] != "placeholder":
                print(
                    f"  [{v['status']}] {k}  "
                    f"({v.get('replaced_at') or '-'}, "
                    f"{v.get('improved_with') or '-'})"
                )

    # Exit non-zero if any placeholders remain — useful for release
    # gates: `audit_placeholders.py && release.sh`
    return 0 if total_placeholder == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
