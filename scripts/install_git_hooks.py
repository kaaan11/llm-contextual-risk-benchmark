#!/usr/bin/env python3
"""Installs git pre-commit hook to enforce research integrity and protocol verification."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = ROOT / ".git" / "hooks"
PRE_COMMIT_HOOK = HOOKS_DIR / "pre-commit"

HOOK_SCRIPT = """#!/usr/bin/env bash
set -e

echo "=== [PRE-COMMIT] Araştırma ve Protokol Doğrulaması Başlatılıyor ==="

# 1. Dondurulmuş protokol ve veri seti hash kontrolü
echo "-> 1/3: Dondurulmuş protokol hash kontrolü..."
python3 scripts/freeze_phase7e_preregistration.py > /dev/null

# 2. Phase 7E ve 7G tutarlılık kontrolü
echo "-> 2/3: Phase 7E ve Phase 7G doğrulayıcıları..."
python3 scripts/validate_phase7e_review.py > /dev/null
python3 scripts/validate_phase7g_review.py > /dev/null

# 3. Temel regresyon ve bütünlük testleri
echo "-> 3/3: Hızlı regresyon testleri..."
if [ -d ".venv" ]; then
    .venv/bin/pytest -q tests/test_dataset_validation.py tests/test_schema_v02.py tests/test_annotate_blind.py tests/test_phase7g_tooling.py > /dev/null
else
    python3 -m unittest discover -s tests -p "test_dataset_validation.py" > /dev/null
fi

echo "=== [PRE-COMMIT] ✅ Tüm Bütünlük Kontrolleri Geçti. Commit Onaylandı. ==="
exit 0
"""


def install_hooks() -> int:
    if not (ROOT / ".git").exists():
        print("Hata: .git dizini bulunamadı.")
        return 1

    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    PRE_COMMIT_HOOK.write_text(HOOK_SCRIPT, encoding="utf-8")
    PRE_COMMIT_HOOK.chmod(0o755)
    print(f"✓ Git pre-commit hook başarıyla kuruldu: {PRE_COMMIT_HOOK}")
    return 0


if __name__ == "__main__":
    sys.exit(install_hooks())
