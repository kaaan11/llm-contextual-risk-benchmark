#!/usr/bin/env python3
"""Phase 7G — Interactive Adjudication CLI Wizard.

Resolves disagreements between rater_a and rater_b on blind isolated prompts,
recording the adjudicated valence and written rationale per the R2 mandate.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.apply_phase7g_annotations import (
    BLIND,
    HISTORY,
    KEY,
    SNAPS,
    VALENCE_SCALE,
    _load,
    append_history,
    record_adjudication,
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


def get_disagreements(blind_data: dict) -> list[dict]:
    return [
        item for item in blind_data.get("items", [])
        if item.get("annotation_status") == "DISAGREEMENT_PENDING_ADJUDICATION"
    ]


def run_adjudication_wizard(
    reviewer_id: str,
    reviewer_role: str | None = None,
    limit: int | None = None,
    input_func=input,
) -> int:
    blind_data = _load(BLIND)
    key_data = _load(KEY)

    disagreements = get_disagreements(blind_data)
    total = len(disagreements)

    if total == 0:
        print("✓ Çözüm bekleyen bir rater uyuşmazlığı bulunmamaktadır.")
        return 0

    print("=" * 70)
    print(f"Phase 7G Hakemlik (Adjudication) Sihirbazı — Hakem: {reviewer_id}")
    print(f"Uyuşmazlık Bulunan Madde Sayısı: {total}")
    print("=" * 70)
    print("Seçenekler: [1..5] Nihai Karar | [q] Çıkış\n")

    recorded_count = 0

    for idx, item in enumerate(disagreements, start=1):
        if limit is not None and recorded_count >= limit:
            break

        bid = item["blind_id"]
        prompt = item["canonical_final_prompt"]
        ra = item.get("rater_a", {})
        rb = item.get("rater_b", {})

        print(f"\n--- [{idx}/{total}] {bid} ---")
        print(f"Prompt:\n\"{prompt}\"\n")
        print(f"Rater A ({ra.get('reviewer_id', 'anon')}): {ra.get('isolated_prompt_valence_observed')} (Güven: {ra.get('reviewer_confidence')})")
        if ra.get("reviewer_notes"):
            print(f"   Not: {ra.get('reviewer_notes')}")
        print(f"Rater B ({rb.get('reviewer_id', 'anon')}): {rb.get('isolated_prompt_valence_observed')} (Güven: {rb.get('reviewer_confidence')})")
        if rb.get("reviewer_notes"):
            print(f"   Not: {rb.get('reviewer_notes')}")

        print("\nNihai Hakem Kararı (Adjudicated Valence):")
        print("  [1] clearly_benign       (Açıkça zararsız / güvenli)")
        print("  [2] probably_benign      (Muhtemelen zararsız)")
        print("  [3] ambiguous_dual_use   (Belirsiz / Çift kullanımlı)")
        print("  [4] probably_concerning  (Muhtemelen riskli / şüpheli)")
        print("  [5] clearly_concerning   (Açıkça yüksek riskli / zararlı)")

        valence_key = None
        while valence_key not in VALENCE_CHOICES:
            val_in = input_func("Hakem Seçimi [1-5 veya q]: ").strip()
            if val_in.lower() == "q":
                print("\nOturum kaydedildi ve sonlandırıldı.")
                return recorded_count
            if val_in in VALENCE_CHOICES:
                valence_key = val_in
            else:
                print("Geçersiz seçim. Lütfen 1-5 arasında bir rakam veya q girin.")

        valence = VALENCE_CHOICES[valence_key]

        rationale = ""
        while not rationale:
            rationale = input_func("Hakemlik Gerekçesi (Zorunlu): ").strip()
            if not rationale:
                print("Hata: Uyuşmazlık çözümü için yazılı gerekçe zorunludur.")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        entry = {
            "blind_id": bid,
            "adjudicated_valence": valence,
            "rationale": rationale,
        }

        events = record_adjudication(
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
        print(f"✓ {bid} için hakem kararı kaydedildi -> {valence}")

    print(f"\nİşlem tamamlandı: {recorded_count} adet uyuşmazlık çözüldü.")
    return recorded_count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Phase 7G Interactive Adjudication CLI")
    parser.add_argument("--reviewer-id", required=True, help="Unique identifier of the adjudicator")
    parser.add_argument("--reviewer-role", default="researcher_adjudication", help="Optional role description")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of items to adjudicate this run")

    args = parser.parse_args(argv)
    with review_lock(BLIND.parent):
        run_adjudication_wizard(args.reviewer_id, args.reviewer_role, limit=args.limit)


if __name__ == "__main__":
    main()
