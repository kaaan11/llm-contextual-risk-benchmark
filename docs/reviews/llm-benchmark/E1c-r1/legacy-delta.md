# E1c-R1 — Legacy delta (yalnız etkilenen satırlar)

**Statü: DRAFT / NOT EFFECTIVE.** `../E1c/legacy-to-proposed.md` değişmedi; bu dosya yalnız
R1'den etkilenen satırları revize eder + 3 satır ekler. Diğer 11 satır aynen geçerlidir.

## Revize satırlar

| # | Eski statü (E1c) | R1 sonrası statü | Fark |
| --- | --- | --- | --- |
| L-05 | McNemar ikincile indirildi (ad değişikliğiyle) | **Aynı + payda notu:** error-asymmetry endpointinin pay/paydası §2 E-harm tekniğiyle (uygulanabilir ikili görüşler) hesaplanır; `uncertain`/gap DAHİL DEĞİLDİR (H-U seçenekleri endpoint'e taşınır) | Payda kapandı |
| L-09 | Clopper–Pearson korunur | **Kapsam daraltıldı:** YALNIZ tek-oran çıktıları; eşleşmiş farklarda kullanılmaz (§5 O-C1) | Exact vaadi kalktı |
| L-12 | Exclusion/missing kapalı liste | **Aynı + job kimliği:** duplicate tanımı §3 canonical job anahtarına bağlandı | Kimlik kapandı |

## Ek satırlar

| # | Kural | Statü | Gerekçe |
| --- | --- | --- | --- |
| L-16 | Denominator seçenekleri (H-U1/H-U2, H-T1a/H-T1b, D-A/D-B) | **SEÇENEKLİ (onaysız)** | Sonuç değiştirir; E6a'ya bırakılamaz |
| L-17 | Canonical logical job + attempt/gözlem ayrımı | **YENİ (öneri)** | Duplicate/model-run karışması kapanır; alan sahipliği E5a/E5c |
| L-18 | `stratified_by_assistant_stance` zorunlu ekseni | **YENİ (AGENTS.md zorunluluğu)** | Kategori ekseninden ayrı; havuzlama yok |

## Değişmeyenler

L-01–L-04, L-06–L-08, L-10, L-11, L-13–L-15 E1c'deki halleriyle geçerlidir.
