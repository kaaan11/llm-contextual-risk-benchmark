#!/usr/bin/env python3
"""Phase 7G — Inter-Rater Agreement & Divergence Analyzer.

Computes 5x5 confusion matrix, percent agreement, unweighted and weighted Cohen's Kappa,
and highlights severe rating divergences (|delta| >= 2) between rater_a and rater_b.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

AUDIT = ROOT / "results" / "dataset_audit"
BLIND_FILE = AUDIT / "phase7g_blind_review.json"

SCALE = [
    "clearly_benign",
    "probably_benign",
    "ambiguous_dual_use",
    "probably_concerning",
    "clearly_concerning",
]
SCALE_INDEX = {val: idx for idx, val in enumerate(SCALE)}


def load_blind_data(p: Path = BLIND_FILE) -> list[dict]:
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("items", [])


def compute_agreement_stats(items: list[dict]) -> dict:
    paired = []
    for item in items:
        ra = item.get("rater_a", {}).get("isolated_prompt_valence_observed")
        rb = item.get("rater_b", {}).get("isolated_prompt_valence_observed")
        if ra in SCALE_INDEX and rb in SCALE_INDEX:
            paired.append({
                "blind_id": item["blind_id"],
                "prompt": item.get("canonical_final_prompt", ""),
                "ra_val": ra,
                "rb_val": rb,
                "ra_idx": SCALE_INDEX[ra],
                "rb_idx": SCALE_INDEX[rb],
                "delta": abs(SCALE_INDEX[ra] - SCALE_INDEX[rb]),
                "ra_notes": item.get("rater_a", {}).get("reviewer_notes"),
                "rb_notes": item.get("rater_b", {}).get("reviewer_notes"),
            })

    n = len(paired)
    if n == 0:
        return {"n_paired": 0}

    # 5x5 Confusion Matrix
    matrix = [[0] * 5 for _ in range(5)]
    for p in paired:
        matrix[p["ra_idx"]][p["rb_idx"]] += 1

    # Exact agreement
    po = sum(matrix[i][i] for i in range(5)) / n

    # Marginal probabilities
    p_ra = [sum(matrix[i][j] for j in range(5)) / n for i in range(5)]
    p_rb = [sum(matrix[i][j] for i in range(5)) / n for j in range(5)]
    pe = sum(p_ra[i] * p_rb[i] for i in range(5))

    unweighted_kappa = None if pe >= 1.0 else (po - pe) / (1.0 - pe)

    # Linear & Quadratic Weighted Kappa
    w_lin_sum = 0.0
    we_lin_sum = 0.0
    w_quad_sum = 0.0
    we_quad_sum = 0.0
    k = 5

    for i in range(k):
        for j in range(k):
            w_lin = 1.0 - abs(i - j) / (k - 1)
            w_quad = 1.0 - ((i - j) ** 2) / ((k - 1) ** 2)

            observed = matrix[i][j] / n
            expected = p_ra[i] * p_rb[j]

            w_lin_sum += w_lin * observed
            we_lin_sum += w_lin * expected
            w_quad_sum += w_quad * observed
            we_quad_sum += w_quad * expected

    kappa_linear = None if we_lin_sum >= 1.0 else (w_lin_sum - we_lin_sum) / (1.0 - we_lin_sum)
    kappa_quad = None if we_quad_sum >= 1.0 else (w_quad_sum - we_quad_sum) / (1.0 - we_quad_sum)

    severe_divergences = [p for p in paired if p["delta"] >= 2]

    return {
        "n_paired": n,
        "percent_agreement": round(po * 100, 2),
        "pe": round(pe * 100, 2),
        "unweighted_kappa": round(unweighted_kappa, 4) if unweighted_kappa is not None else None,
        "linear_weighted_kappa": round(kappa_linear, 4) if kappa_linear is not None else None,
        "quadratic_weighted_kappa": round(kappa_quad, 4) if kappa_quad is not None else None,
        "confusion_matrix": matrix,
        "severe_divergences": severe_divergences,
    }


def print_agreement_dashboard(stats: dict) -> None:
    print("\n" + "═" * 72)
    print("      PHASE 7G: İKİ-RATER UYUM VE SAPMA ANALİZ RAPORU")
    print("═" * 72)

    n = stats["n_paired"]
    if n == 0:
        print("\n⚠️  Henüz her iki rater (rater_a ve rater_b) tarafından ortak tamamlanmış")
        print("    bir madde bulunmuyor. İkinci rater incelemeleri başladığında bu panel")
        print("    canlı uyum istatistiklerini ve sapmaları hesaplayacaktır.")
        print("\nİnceleme başlatmak için: python3 scripts/annotate_blind.py --rater rater_b --reviewer-id <ad>")
        print("═" * 72 + "\n")
        return

    print(f"\nİkili Değerlendirilmiş Madde Sayısı (N): {n}")
    print(f" • Ham Uyuşum (Percent Agreement): %{stats['percent_agreement']:.1f}")
    print(f" • Beklenen Uyuşum (Chance Agreement, Pe): %{stats['pe']:.1f}")

    uk = stats['unweighted_kappa']
    lk = stats['linear_weighted_kappa']
    qk = stats['quadratic_weighted_kappa']

    def fmt_k(k_val):
        if k_val is None:
            return "Hesaplanamadı"
        interp = "Mükemmel" if k_val >= 0.8 else ("İyi" if k_val >= 0.6 else ("Orta" if k_val >= 0.4 else "Zayıf"))
        return f"{k_val:.4f} ({interp})"

    print(f" • Standart Cohen's Kappa:      {fmt_k(uk)}")
    print(f" • Lineer Ağırlıklı Kappa:     {fmt_k(lk)}")
    print(f" • Kuadratik Ağırlıklı Kappa:  {fmt_k(qk)}")

    print("\n" + "─" * 72)
    print("5x5 ÇAPRAZ GEÇİŞ TABLOSU (CONFUSION MATRIX):")
    print("Satırlar: Rater A | Sütunlar: Rater B")
    short_names = ["c_ben", "p_ben", "ambig", "p_con", "c_con"]
    header = "          " + " ".join(f"{s:>7}" for s in short_names) + "   [Toplam]"
    print(header)

    matrix = stats["confusion_matrix"]
    for i, row in enumerate(matrix):
        row_str = f"{short_names[i]:>8}: " + " ".join(f"{val:>7}" for val in row) + f"   [{sum(row):>4}]"
        print(row_str)

    col_totals = [sum(matrix[r][c] for r in range(5)) for c in range(5)]
    print(" [Toplam]: " + " ".join(f"{c:>7}" for c in col_totals) + f"   [{n:>4}]")

    divs = stats["severe_divergences"]
    print("\n" + "─" * 72)
    if not divs:
        print("✅ Kritik Sapma (|Δ| >= 2) Tespit Edilmedi.")
    else:
        print(f"⚠️  KRİTİK SAPMALAR (|Δ| >= 2) — Toplam: {len(divs)} Madde")
        for d in divs:
            print(f"\n • {d['blind_id']}: Fark = {d['delta']} basamak")
            print(f"   Prompt: \"{d['prompt'][:75]}...\"")
            print(f"   Rater A: {d['ra_val']} | Rater B: {d['rb_val']}")
            if d['ra_notes'] or d['rb_notes']:
                print(f"   Notlar: A: {d['ra_notes']} | B: {d['rb_notes']}")

    print("═" * 72 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 7G Inter-Rater Agreement Analyzer")
    parser.add_argument("--json", action="store_true", help="Output raw JSON stats")
    args = parser.parse_args()

    items = load_blind_data()
    stats = compute_agreement_stats(items)

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print_agreement_dashboard(stats)


if __name__ == "__main__":
    main()
