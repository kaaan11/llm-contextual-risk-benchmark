# E1c — Pre-evaluation amendment taslağı (sürümlü)

**Statü: DRAFT / NOT EFFECTIVE — protocol v1.0.2'ye eklenmez, `rules_changed=false`
açıklamasını değiştirmez, mühürlü dosyaları değiştirmez.** Bu metin, onay + freeze sonrası
atanacak yeni protokol sürümünün (numara onayda belirlenir; aşağıda `v1.0.3-draft` yer tutucudur)
taslağıdır. `APPROVED` hüküm yoktur.

## §1 — Kimlik ve yürürlük

- Hedef: `LLM-CTX-PILOT-2026-01`, v1.0.2 → `v1.0.3-draft` (yer tutucu; onayda kesinleşir).
- Tür: `measurement_and_analysis_amendment` — `rules_changed: true` olacaktır (etkinleşince).
- Zamanlama: İlk model yanıtı gözlenmeden ÖNCE onaylanıp dondurulmalıdır. Gözlem sonrası her
  değişiklik yeni sürüm + yeni run gerektirir (frozen amendment kuralı korunur).
- Kapsam: Yalnız `estimand-contract.md` + `legacy-to-proposed.md` kuralları. Stimulus baytları,
  QC kayıtları, audit geçmişi değişmez. `v1.0.2` belgeleri arşivde aynen korunur.

## §2 — Eski→yeni fark listesi (özet; ayrıntı `legacy-to-proposed.md`)

1. Ordinal Δ aritmetiği → kaldırıldı; yerine madde-eşit nominal dağılım kontrastları (E-act).
2. D-state makinesi → kaldırıldı; yerine D kohortu matched kontrastları (length/priming dili).
3. `context_effect_observed` → kaldırıldı (en fazla arşiv dili); yerine E-harm/E-util + transition.
4. Wilcoxon (destek dahil) → kaldırıldı; yerine transition + exact CI (+ opsiyonel sign testi).
5. McNemar → ikincile indirildi, adı *error-asymmetry*; korunması insan kararı.
6. Modal kural → ikincil betimleme; tüm geçerli tekrarlar korunur.
7. H3/F4 → §5 seçenekleriyle revize (sıfır çakışması giderilir).
8. Eşik dili → kaldır (Öneri) veya pre-set δ (TBD).
9. Exclusion/missing → kapalı liste + koşula-göre raporlama + 0/0 yasağı.
10. Multiplicity → frozen beyan korunur; yeni confirmatory ayrı amendment ister.

Her maddenin gerekçesi `legacy-to-proposed.md` tablosundadır. Eski metinler silinmez;
"superseded" damgasıyla arşivlenir.

## §3 — Etkilenen hipotezler ve geçiş

- H1: `context_effect_observed` payı → E ailesi DU kontrastları + tabakalı sunum (eşik §5'te).
- H2: disposition medyanı → E-util B−A + harm ayrımı.
- H3: §5 seçenekleri (harm-dili strict veya confirmatory-dışı).
- H0a: null-kontrol farkı → tabakalı kontrast farkları (havuzlama yok).
- H0b: D-state → D kohort matched sonucu.
- H0c: ters-yön → E-util/E-harm yön okuması.
- F1–F6: §7 haritasıyla (F6 blind-gate sonuçları aynen raporlanır).

## §4 — Yürürlük koşulları (onay öncesi tamamlanacak)

- [ ] İnsan araştırmacı: birincil endpoint ailesi (R-E1), McNemar'ın akıbeti (R-E2), CI yöntemi,
  H3/F4 seçeneği, eşik dili, D-A/D-B paydası, criterion içerikleri, E1b kategori/alan onayı.
- [ ] `v1.0.3` numarası + yürürlük tarihi + imza (boş; insan doldurur).
- [ ] E5 schedule + E6 analiz provası bu sözleşmeye bağlanmadan E5/E6'ya devir YOKTUR.
- [ ] Freeze: composite yeniden üretilir; eski mühür sessizce değiştirilmez.

## §5 — İmza (boş)

```
researcher_id        : <doldurulmadı>
decision             : <PENDING>
timestamp            : <doldurulmadı>
protocol_version_new : <v1.0.3-draft yer tutucu>
```
