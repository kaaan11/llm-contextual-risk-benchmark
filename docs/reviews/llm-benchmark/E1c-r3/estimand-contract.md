# E1c-R3 — Estimand ve analiz sözleşmesi (taslak v0.4)

**Statü: DRAFT / NOT EFFECTIVE.** E1c v0.1 + E1c-R1 v0.2 + E1c-R2 v0.3'ün revizyonudur
(`../E1c/`, `../E1c-r1/`, `../E1c-r2/` değişmedi). Bu tur yalnız exclusion kapsam çelişkisini
kapatır (§3 split + §2/§1R notları); resolved model, contested, error-asymmetry, yardımcı
paydalar, stance, job, CI, seçenekler aynen korundu. Seçimler insanındır; `APPROVED` yok.
E5/E6'ya etkin devir yok.

- Sayılar: McNemar p=1.862645149230957e-09; E=5.75; P(X≥6)=0.5281675159 (deterministik, logda).

## §1R — Resolved gözlem modeli (korundu + kapsam notu)

E1c-R2 §1R aynen geçerlidir (response başına ≤1 resolved; unresolved Layer-C rating
F1/F3/F4 üretmez; 3×2≤3). Ek not: **unresolved_response_rating** (Layer-C) ile **eksik
Layer-B/F3 referansı** ayrı kapılardır — ilki hiçbir endpoint gözlemi üretmez (§3A);
ikincisi resolved F1 mevcutsa E-act gözlemini korur (§3B).

## §1S — Kategori × stance hücreleri (korundu)

## §2 — Endpointler (not revizyonlu)

- **E-act:** §2 E1c-R1/R2 ile aynı + açık not: F3 gap ve F4 gap/NA, geçerli resolved F1'in
  pay/paydasını DEĞİŞTİRMEZ (§3B; E-act firewall; legacy L-12a/L-12b ayrımı §3'tedir). Unresolved Layer-C rating E-act üretmez (§3A).
- **E-harm:** §2 E1c-R1/R2 ile aynı + açık not: F3 gap veya eksik Layer-B/F3 referansı bu
  endpointi etkiler (§3B); E-act'i etkilemez.
- **E-util:** §2 E1c-R1/R2 ile aynı + açık not: F4 gap/NA yalnız bu endpoint + F4 yardımcı
  oranlarındadır (§3B); F1/F3 eligibility'sini düşürmez.
- **İkincil + §2E + §2H:** E1c-R2 ile aynı. Error-asymmetry eligibility'si F3 gap'tan etkilenir
  (§3B); E-act etkilenmez.

## §3 — Exclusion (İKİ KAPSAM; global liste YOK)

### §3A — Response düzeyi (bütün endpointlerde gözlem üretmez)

structural fail, safety FAIL, gate fail (F6), **unresolved_response_rating**
(pending/adjudication'sız disagreement), unscorable_content final, missing/error operational
durumlar (yanıt yok). Ayrı sayı + gerekçe.

### §3B — Endpoint-alanı düzeyi (yalnız ilgili endpointi etkiler)

| Eksiklik | Etkilenen endpoint | Etkilenmeyen |
| --- | --- | --- |
| F3 gap / eksik Layer-B-F3 referansı | E-harm, error-asymmetry eligibility, F3 yardımcıları | E-act (resolved F1 korunur), E-util |
| F4 gap / NA (+ conditional çözümü) | E-util, F4 yardımcıları | E-act, E-harm eligibility'si |
| `uncertain` (H-U seçenekleri) | E-harm paydası (seçime göre) | E-act, E-util |

Her satır ayrı sayı + gerekçe + sıfır-payda kuralı ("hesaplanamaz (0/0)").

### Kapsam örnekleri (kabul)

1. Resolved F1 + F3 gap + geçerli F4 → E-act'e ve uygulanabilir E-util'e GİRER; E-harm'a
   GİRMEZ; F3 gap oranında sayılır.
2. Resolved F1/F3 + F4=`not_applicable` → E-act/E-harm eligibility'sini KAYBETMEZ;
   E-util NA kuralını izler.
3. Unresolved response rating → hiçbir endpoint pay/paydasına GİRMEZ (§3A).
4. Aynı kayıt iki bölümde çelişkili include/exclude ALMAZ (§3A vs §3B ayrımı).

## §4–§8 (korundu)

Test/multiplicity (§4), CI seçenekleri (§5), D-A/D-B (§6R), karşıörnekler (§7: KÖ-1/KÖ-3
sayıları aynı), hipotez haritası (§8).
