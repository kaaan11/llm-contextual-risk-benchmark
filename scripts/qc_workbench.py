#!/usr/bin/env python3
"""Phase 7G — Master Human Quality Control Workbench.

Unified terminal control center providing access to all Phase 7G review workflows:
blind prompt annotation, adjudication, context/safety review, and final decisions.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.phase7g_status import print_dashboard
from scripts.phase7g_agreement import compute_agreement_stats, print_agreement_dashboard, load_blind_data
from scripts.annotate_blind import run_wizard as run_blind_wizard
from scripts.adjudicate_blind import run_adjudication_wizard
from scripts.review_context import run_context_wizard
from scripts.decide_phase7g import run_decide_wizard


def get_reviewer_id(default_prompt: str = "İnceleyen / Rater Kimliğiniz: ") -> str:
    rid = ""
    while not rid:
        rid = input(default_prompt).strip()
        if not rid:
            print("Kimlik boş bırakılamaz.")
    return rid


def run_validators() -> None:
    print("\nDoğrulama scriptleri çalıştırılıyor...")
    cmd_e = [sys.executable, str(ROOT / "scripts" / "validate_phase7e_review.py")]
    cmd_g = [sys.executable, str(ROOT / "scripts" / "validate_phase7g_review.py")]
    res_e = subprocess.run(cmd_e, cwd=ROOT)
    res_g = subprocess.run(cmd_g, cwd=ROOT)
    if res_e.returncode == 0 and res_g.returncode == 0:
        print("\n✅ TÜM DOĞRULAYICILAR BAŞARILI (VALID).")
    else:
        print("\n❌ DOĞRULAMA HATALARI BULUNDU.")


def main_menu() -> None:
    while True:
        print("\n" + "═" * 72)
        print("          PHASE 7G HUMAN QUALITY CONTROL WORKBENCH")
        print("═" * 72)
        print(" [1] Durum ve İlerleme Raporu (Dashboard & Gate Check)")
        print(" [2] Kör İnceleme Yap — Rater A (Isolated Prompt Annotation)")
        print(" [3] Kör İnceleme Yap — Rater B (Isolated Prompt Annotation)")
        print(" [4] Uyuşmazlıkları Çöz (Adjudicate Disagreements)")
        print(" [5] Bağlam, Güvenlik ve Doğallık İncelemesi (Context Review)")
        print(" [6] Nihai Araştırmacı Kararlarını Ver (Decide KEEP/REVISE/REJECT)")
        print(" [7] İki-Rater Uyum ve Sapma Analizi (Cohen's Kappa & Confusion Matrix)")
        print(" [8] Veri Bütünlüğü ve QC Doğrulayıcılarını Çalıştır (Validate)")
        print(" [q] Çıkış")
        print("═" * 72)

        choice = input("Seçiminiz [1-8 veya q]: ").strip().lower()

        if choice == "q":
            print("\nQC Workbench kapatıldı.")
            break
        elif choice == "1":
            print_dashboard()
        elif choice == "2":
            rid = get_reviewer_id("Rater A Kimliğiniz (örn. rater_1 / adınız): ")
            run_blind_wizard("rater_a", rid)
        elif choice == "3":
            rid = get_reviewer_id("Rater B Kimliğiniz (bağımsız rater kimliği): ")
            run_blind_wizard("rater_b", rid)
        elif choice == "4":
            rid = get_reviewer_id("Hakem Kimliğiniz: ")
            run_adjudication_wizard(rid)
        elif choice == "5":
            rid = get_reviewer_id("Araştırmacı Kimliğiniz: ")
            run_context_wizard(rid)
        elif choice == "6":
            rid = get_reviewer_id("Baş Araştırmacı Kimliğiniz: ")
            run_decide_wizard(rid)
        elif choice == "7":
            items = load_blind_data()
            print_agreement_dashboard(compute_agreement_stats(items))
        elif choice == "8":
            run_validators()
        else:
            print("Geçersiz seçim. Lütfen 1-8 arasında bir rakam veya q girin.")


if __name__ == "__main__":
    main_menu()
