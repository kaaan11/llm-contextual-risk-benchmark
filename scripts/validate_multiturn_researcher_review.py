"""Phase 7C-REVIEW bağımsız review JSON validator'ı."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_multiturn_researcher_review import validate_review  # noqa: E402


DEFAULT_REVIEW = ROOT / "results" / "dataset_audit" / "multiturn_researcher_review.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 7C researcher review JSON")
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    args = parser.parse_args(argv)
    try:
        review = json.loads(args.review.read_text(encoding="utf-8"))
        report = validate_review(review)
    except (OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
        print(f"Review validation başarısız: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
