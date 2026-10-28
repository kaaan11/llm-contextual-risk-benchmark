#!/usr/bin/env python3
"""Phase 7G — Interactive CLI Wizard for Blind Isolated-Prompt Annotations.

Allows human raters (rater_a or rater_b) to evaluate canonical final prompts
sequentially in a distraction-free terminal workflow without manually editing JSON.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.apply_phase7g_annotations import (
    BLIND,
    CONFIDENCE,
    HISTORY,
    KEY,
    SNAPS,
    VALENCE_SCALE,
    _load,
    append_history,
    record_blind,
    snapshot,
)
from scripts.review_store import commit_state_and_history, review_lock
from scripts.refresh_phase7g_rollups import main as refresh_rollups


VALENCE_CHOICES = {
    "1": "clearly_benign",
    "2": "probably_benign",
    "3": "ambiguous_dual_use",
    "4": "probably_concerning",
    "5": "clearly_concerning",
}

CONFIDENCE_CHOICES = {
    "1": "high",
    "2": "medium",
    "3": "low",
}


def get_pending_items(blind_data: dict, rater: str) -> list[dict]:
    pending = []
    for item in blind_data.get("items", []):
        rater_slot = item.get(rater, {})
        if rater_slot.get("isolated_prompt_valence_observed") is None:
            pending.append(item)
    return pending


def run_wizard(
    rater: str,
    reviewer_id: str,
    reviewer_role: str | None = None,
    limit: int | None = None,
    input_func=input,
) -> int:
    blind_data = _load(BLIND)
    key_data = _load(KEY)

    pending = get_pending_items(blind_data, rater)
    total_pending = len(pending)

    if total_pending == 0:
        print(f"✓ '{rater}' için bekleyen kör anotasyon bulunmamaktadır. Tüm maddeler tamamlandı.")
        return 0

    print("=" * 70)
    print(f"Phase 7G Kör İnceleme Sihirbazı — Rater: {rater} ({reviewer_id})")
    print(f"Toplam Tamamlanacak Madde: {total_pending}")
    print("=" * 70)
    print("Seçenekler: [1..5] Karar | [q] Kaydet ve Çık\n")

    recorded_count = 0

    for idx, item in enumerate(pending, start=1):
        if limit is not None and recorded_count >= limit:
            break

        bid = item["blind_id"]
        prompt = item["canonical_final_prompt"]

        print(f"\n--- [{idx}/{total_pending}] {bid} ---")
        print(f"Prompt:\n\"{prompt}\"\n")
        print("Valence Seçimi:")
        print("  [1] clearly_benign       (Açıkça zararsız / güvenli)")
        print("  [2] probably_benign      (Muhtemelen zararsız)")
        print("  [3] ambiguous_dual_use   (Belirsiz / Çift kullanımlı)")
        print("  [4] probably_concerning  (Muhtemelen riskli / şüpheli)")
        print("  [5] clearly_concerning   (Açıkça yüksek riskli / zararlı)")

        valence_key = None
        while valence_key not in VALENCE_CHOICES:
            val_in = input_func("Seçiminiz [1-5 veya q]: ").strip()
            if val_in.lower() == "q":
                print("\nOturum kaydedildi ve sonlandırıldı.")
                return recorded_count
            if val_in in VALENCE_CHOICES:
                valence_key = val_in
            else:
                print("Geçersiz seçim. Lütfen 1-5 arasında bir rakam veya q girin.")

        valence = VALENCE_CHOICES[valence_key]

        conf_in = input_func("Güven derecesi [1: high (varsayılan), 2: medium, 3: low]: ").strip()
        confidence = CONFIDENCE_CHOICES.get(conf_in, "high")

        notes = input_func("İsteğe bağlı not (boş bırakılabilir): ").strip()
        notes = notes if notes else None

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        entry = {
            "blind_id": bid,
            "rater": rater,
            "valence": valence,
            "confidence": confidence,
            "notes": notes,
        }

        # apply_phase7g_annotations API
        events = record_blind(
            blind_data,
            key_data,
            [entry],
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            timestamp=timestamp,
        )

        clean_stamp = timestamp.replace(":", "")
        snap = SNAPS / f"phase7g_blind_review.{clean_stamp}.json"
        commit_state_and_history(BLIND, blind_data, HISTORY, events, snap)
        refresh_rollups()
        recorded_count += 1
        print(f"✓ {bid} başarıyla kaydedildi.")

    print(f"\nİşlem tamamlandı: {recorded_count} adet kayıt işlendi.")
    return recorded_count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Phase 7G Interactive Blind Annotation CLI")
    parser.add_argument("--rater", choices=["rater_a", "rater_b"], required=True, help="Rater slot")
    parser.add_argument("--reviewer-id", required=True, help="Unique identifier of the rater")
    parser.add_argument("--reviewer-role", default=None, help="Optional role description")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of items to annotate this run")

    args = parser.parse_args(argv)
    with review_lock(BLIND.parent):
        run_wizard(args.rater, args.reviewer_id, args.reviewer_role, limit=args.limit)


if __name__ == "__main__":
    main()
