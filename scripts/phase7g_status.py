#!/usr/bin/env python3
"""Phase 7G — Terminal Live Status Dashboard.

Provides an instant visual overview of human quality control progress,
inter-rater agreement, context reviews, and blockers to Phase 8.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "dataset_audit"
BLIND = AUDIT / "phase7g_blind_review.json"
QC = AUDIT / "phase7g_human_qc.json"


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def get_status_report() -> dict:
    blind = load_json(BLIND)
    qc = load_json(QC)

    items = blind.get("items", [])
    total = len(items)

    rater_a_done = sum(1 for i in items if i.get("rater_a", {}).get("isolated_prompt_valence_observed") is not None)
    rater_b_done = sum(1 for i in items if i.get("rater_b", {}).get("isolated_prompt_valence_observed") is not None)
    both_done = sum(1 for i in items if (
        i.get("rater_a", {}).get("isolated_prompt_valence_observed") is not None and
        i.get("rater_b", {}).get("isolated_prompt_valence_observed") is not None
    ))

    agreed = 0
    disagreed = 0
    for i in items:
        va = i.get("rater_a", {}).get("isolated_prompt_valence_observed")
        vb = i.get("rater_b", {}).get("isolated_prompt_valence_observed")
        if va is not None and vb is not None:
            if va == vb:
                agreed += 1
            else:
                disagreed += 1

    adjudicated = sum(1 for i in items if i.get("adjudicated_valence") is not None)
    disagreements_pending = sum(1 for i in items if i.get("annotation_status") == "DISAGREEMENT_PENDING_ADJUDICATION")

    qc_items = qc.get("items", [])
    context_done = sum(1 for i in qc_items if i.get("context_review", {}).get("status") == "COMPLETE")
    safety_pass = sum(1 for i in qc_items if i.get("safety_review", {}).get("safety_status") == "PASS")
    safety_fail = sum(1 for i in qc_items if i.get("safety_review", {}).get("safety_status") == "FAIL")

    decisions = {"KEEP": 0, "REVISE": 0, "REJECT": 0, "PENDING": 0}
    for i in qc_items:
        d = i.get("stimulus_review_status", "PENDING")
        decisions[d] = decisions.get(d, 0) + 1

    phase_complete = qc.get("phase_complete", False)

    blockers = []
    if rater_a_done < total:
        blockers.append(f"rater_a eksik: {total - rater_a_done} madde bekleniyor")
    if rater_b_done < total:
        blockers.append(f"rater_b eksik: {total - rater_b_done} madde bekleniyor")
    if disagreements_pending > 0:
        blockers.append(f"Çözülmemiş uyuşmazlık: {disagreements_pending} madde hakem kararı (adjudication) bekliyor")
    if context_done < total:
        blockers.append(f"Bağlam ve güvenlik incelemesi eksik: {total - context_done} madde bekleniyor")
    if decisions["KEEP"] + decisions["REJECT"] < total:
        blockers.append(f"Nihai araştırmacı kararı eksik: {decisions['PENDING']} madde PENDING durumda")
    if not blockers:
        ready_for_phase8 = True
    else:
        ready_for_phase8 = False

    return {
        "total": total,
        "rater_a_done": rater_a_done,
        "rater_b_done": rater_b_done,
        "both_done": both_done,
        "agreed": agreed,
        "disagreed": disagreed,
        "disagreements_pending": disagreements_pending,
        "adjudicated": adjudicated,
        "context_done": context_done,
        "safety_pass": safety_pass,
        "safety_fail": safety_fail,
        "decisions": decisions,
        "phase_complete": phase_complete,
        "ready_for_phase8": ready_for_phase8,
        "blockers": blockers,
    }


def print_dashboard() -> None:
    rep = get_status_report()
    t = rep["total"]

    print("\n" + "═" * 72)
    print("        PHASE 7G: İNSAN KALİTE KONTROLÜ (HUMAN QC) DURUM RAPORU")
    print("═" * 72)

    def pbar(val: int, total: int, width: int = 25) -> str:
        ratio = (val / total) if total > 0 else 0
        filled = int(width * ratio)
        return f"[{'█' * filled}{'░' * (width - filled)}] {val}/{total} ({ratio * 100:.1f}%)"

    print("\n1. KÖR İZOLE PROMPT İNCELEMESİ (TWO-RATER GATE):")
    print(f"   • Rater A İlerlemesi: {pbar(rep['rater_a_done'], t)}")
    print(f"   • Rater B İlerlemesi: {pbar(rep['rater_b_done'], t)}")
    print(f"   • Her İki Rater Hazır: {rep['both_done']}/{t}")
    if rep["both_done"] > 0:
        print(f"     └─ Tam Uyuşum (Agreement): {rep['agreed']}")
        print(f"     └─ Uyuşmazlık (Disagreement): {rep['disagreed']} (Bekleyen: {rep['disagreements_pending']})")
    print(f"   • ADJUDICATED Durumu: {pbar(rep['adjudicated'], t)}")

    print("\n2. BAĞLAM, GÜVENLİK VE DOĞALLIK İNCELEMESİ:")
    print(f"   • Bağlam İncelendi:   {pbar(rep['context_done'], t)}")
    print(f"   • Güvenlik Durumu:    PASS: {rep['safety_pass']} | FAIL: {rep['safety_fail']}")

    print("\n3. NİHAİ ARAŞTIRMACI KARARLARI (DECISIONS):")
    d = rep["decisions"]
    print(f"   • KEEP:   {d.get('KEEP', 0):2d} | REVISE: {d.get('REVISE', 0):2d}")
    print(f"   • REJECT: {d.get('REJECT', 0):2d} | PENDING: {d.get('PENDING', 0):2d}")

    print("\n4. PHASE 8 DEĞERLENDİRME KAPISI:")
    if rep["ready_for_phase8"] and rep["phase_complete"]:
        print("   ✅ PHASE 8 İÇİN TÜM KAPILAR AÇIK! Model değerlendirmesi başlatılabilir.")
    else:
        print("   🔒 PHASE 8 KİLİTLİ. Kalan engeller:")
        for b in rep["blockers"]:
            print(f"      - {b}")

    print("\n" + "─" * 72)
    print("Sonraki Adım Kılavuzu:")
    if rep["rater_a_done"] < t:
        print("   python3 scripts/annotate_blind.py --rater rater_a --reviewer-id <adiniz>")
    elif rep["rater_b_done"] < t:
        print("   python3 scripts/annotate_blind.py --rater rater_b --reviewer-id <ikinci_rater>")
    elif rep["disagreements_pending"] > 0:
        print("   python3 scripts/adjudicate_blind.py --reviewer-id <adiniz>")
    elif rep["context_done"] < t:
        print("   python3 scripts/review_context.py --reviewer-id <adiniz>")
    elif d.get("PENDING", 0) > 0:
        print("   python3 scripts/decide_phase7g.py --reviewer-id <adiniz>")
    print("═" * 72 + "\n")


if __name__ == "__main__":
    print_dashboard()
