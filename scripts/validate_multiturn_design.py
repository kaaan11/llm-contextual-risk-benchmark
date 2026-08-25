"""Phase 7C design specification validator.

Mevcut JSON design specification'ı bağımsız olarak doğrular; conversation veya
model evaluation üretmez ve researcher approval eklemez.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_researcher_design import validate_design  # noqa: E402


DEFAULT_DESIGN = ROOT / "dataset" / "pilot" / "multiturn" / "design_specification.json"
DEFAULT_REPORT = ROOT / "results" / "dataset_audit" / "multiturn_design_validation.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 7C researcher-led design")
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    try:
        spec = json.loads(args.design.read_text(encoding="utf-8"))
        report = validate_design(spec)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
        print(f"Design validation başarısız: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
