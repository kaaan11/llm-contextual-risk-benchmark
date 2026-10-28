#!/usr/bin/env python3
"""Phase 7G — Interactive Final Decision CLI Wizard.

Guides the researcher through recording final review decisions (KEEP, REVISE,
REJECT) once all earlier verification gates (blind, context, safety, naturalness)
have been satisfied.
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
    QC,
    QCError,
    SNAPS,
    _load,
    append_history,
    blind_gate_for,
    blind_item_for,
    category_for,
    keep_eligibility,
    record_decision,
    snapshot,
)
from scripts.review_store import commit_state_and_history, review_lock
from scripts.refresh_phase7g_rollups import main as refresh_rollups


def get_pending_decision_items(qc: dict) -> list[dict]:
    return [
        item for item in qc.get("items", [])
        if item.get("review_decision", "PENDING") == "PENDING"
    ]


def run_decide_wizard(
    reviewer_id: str,
    reviewer_role: str | None = None,
    limit: int | None = None,
    input_func=input,
) -> int:
    qc = _load(QC)
    blind = _load(BLIND)
    key = _load(KEY)

    pending = get_pending_decision_items(qc)
    total = len(pending)

    if total == 0:
        print("✓ Karar bekleyen madde bulunmamaktadır. Tüm maddeler karara bağlanmıştır.")
        return 0

    print("=" * 72)
    print(f"Phase 7G Nihai Karar Sihirbazı — Araştırmacı: {reviewer_id}")
    print(f"Karar Bekleyen Madde Sayısı: {total}")
    print("=" * 72)
    print("Seçenekler: [1] KEEP | [2] REVISE | [3] REJECT | [q] Çıkış\n")

    recorded_count = 0

    for idx, item in enumerate(pending, start=1):
        if limit is not None and recorded_count >= limit:
            break

        rid = item["research_item_id"]
        try:
            blind_status, gate_result = blind_gate_for(blind, key, rid)
            blind_item = blind_item_for(blind, key, rid)
            category = category_for(key, rid)
        except QCError as exc:
            print(f"[{idx}/{total}] ARAŞTIRMA MADDESİ: {rid}")
            print(f"  ⚠️  Kör kayıt bulunamadı ({exc}); karar için uygun değildir.")
            continue
        gate_flag = (blind_item or {}).get("gate_flag")
        ctx_status = item.get("context_review", {}).get("status")
        safe_status = item.get("safety_review", {}).get("safety_status")
        nat_status = item.get("naturalness_review", {}).get("naturalness")
        struct_pass = item.get("structural_verification", {}).get("passes")

        print("\n" + "─" * 72)
        print(f"[{idx}/{total}] ARAŞTIRMA MADDESİ: {rid}")
        print(f"  • Kör İnceleme Durumu: {blind_status}")
        print(f"  • Kör Kapı Sonucu:     {gate_result}"
              + (f" ({gate_flag})" if gate_flag else ""))
        print(f"  • Bağlam İncelemesi:   {ctx_status}")
        print(f"  • Güvenlik Durumu:     {safe_status}")
        print(f"  • Doğallık Derecesi:   {nat_status}")
        print(f"  • Yapısal Doğrulama:   {'GEÇTİ' if struct_pass else 'BAŞARISIZ'}")

        eligible_for_keep, _reasons = keep_eligibility(
            item, blind_item, category)

        if not eligible_for_keep:
            print("  ⚠️  Bu madde henüz KEEP kararı için uygun değildir (ön koşullar eksik).")
            print(f"      Eksikler: {', '.join(_reasons)}")
            print("      Yalnızca REVISE veya REJECT kararı verilebilir.")

        dec_in = None
        while dec_in not in {"1", "2", "3", "q"}:
            prompt_str = "Nihai Kararınız [[1] KEEP, [2] REVISE, [3] REJECT, [q] Çıkış]: "
            dec_in = input_func(prompt_str).strip().lower()
            if dec_in == "q":
                print("\nOturum kaydedildi ve sonlandırıldı.")
                return recorded_count
            if dec_in == "1" and not eligible_for_keep:
                print("Hata: Ön koşullar sağlanmadan KEEP kararı verilemez.")
                dec_in = None

        decision = {"1": "KEEP", "2": "REVISE", "3": "REJECT"}[dec_in]

        notes = None
        if decision in {"REVISE", "REJECT"}:
            while not notes:
                notes = input_func(f"{decision} gerekçesi (zorunlu): ").strip()
        else:
            note_raw = input_func("Onay notu (isteğe bağlı): ").strip()
            notes = note_raw if note_raw else None

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "research_item_id": rid,
            "decision": decision,
            "notes": notes,
        }

        events = record_decision(
            qc,
            blind,
            key,
            [payload],
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            timestamp=timestamp,
        )

        clean_stamp = timestamp.replace(":", "")
        snap = SNAPS / f"phase7g_human_qc.{clean_stamp}.json"
        commit_state_and_history(QC, qc, HISTORY, events, snap)
        refresh_rollups()
        recorded_count += 1
        print(f"✓ {rid} için nihai karar kaydedildi -> {decision}")

    print(f"\nİşlem tamamlandı: {recorded_count} adet karar verildi.")
    return recorded_count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Phase 7G Interactive Decision CLI")
    parser.add_argument("--reviewer-id", required=True, help="Unique identifier of the researcher")
    parser.add_argument("--reviewer-role", default="lead_researcher", help="Optional role description")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of items to decide this run")

    args = parser.parse_args(argv)
    with review_lock(QC.parent):
        run_decide_wizard(args.reviewer_id, args.reviewer_role, limit=args.limit)


if __name__ == "__main__":
    main()
