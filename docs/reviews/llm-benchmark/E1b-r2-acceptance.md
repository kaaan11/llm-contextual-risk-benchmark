# E1b-R2 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1b-R2 KABUL EDİLMEDİ; E1c/E2c KİLİTLİ.**

## Doğrulanan düzeltmeler

[E1b-R2 briefindeki](../../llm-benchmark-E1b-r2-task.md) iki hedef karşılanmıştır:

- `resolved_reference`, iki ham criterion önerisini koruyarak stable ID/version, çözülmüş üçlü,
  resolution source, kaynak slotlar ve kayıt provenance'ı taşır. Pending veya çözülmemiş
  disagreement halinde F3 yasaktır.
- Frozen annotation protocol §6.2 doğru uygulanmıştır: iki explicit `unscorable_content` doğrudan
  final durumu üretir; tek taraflı görüş adjudication'a gider; confidence scoreability üretmez.

Teslimin JSON/JSONL yapısı, sekiz exit-0 komut kaydı ve log hedefleri, checksum manifestosu,
Markdown bağlantıları ve `git diff --check` bağımsız olarak geçti. Stimulus ve 51/5 satırlık
append-only audit geçmişleri kabul edilmiş hashlerle aynıdır. İnsan etiketi, kod veya API çağrısı
yoktur.

## Kalan yapısal blokajlar

### R1 — Response scoreability yanlış katmanda ve zamanda

`scoreable_view`, F5 `condition_reference.slot_schema` içinde bulunuyor. F5 Layer B ve
`pre_evaluation`; `unscorable_content` ise ancak gerçek model response görüldükten sonra iki insan
tarafından verilebilen Layer-C görüşüdür. Mevcut şema model çıktısını görmemesi gereken Layer-B
rater'ından gelecekteki response'un scoreability kararını ister. Üst düzey final-state metni doğru
olsa da bu kararı taşıyacak post-evaluation iki-rater kayıt zarfı yoktur.

Gerekli düzeltme: Layer-B condition-reference slotlarından `scoreable_view` ve
`unscorable_reason` çıkarılmalı. F1–F4 ile scoreability için ayrı Layer-C/post-evaluation
`rater_a`/`rater_b`, provenance, agreement ve gerektiğinde adjudication zarfı tanımlanmalı. Frozen
§6.2 geçişleri bu zarf üzerinde çalışmalıdır. Layer-B körlük/maruziyet kuralı korunmalıdır.

### R2 — `contested` condition kökünden resolved criterion içine taşınmış

E1b-R1'de `contested`, condition düzeyindeki researcher-only statüydü. R2 şemasında F5 kökünde
yoktur ve `resolved_reference` içine gömülmüştür; rubrik ise blokların değişmediğini söylüyor.
Böylece resolved reference `null` iken condition'ın contested statüsü temsil edilemez ve criterion
versiyonlaması condition handling statüsünü yanlışlıkla kapsar.

Gerekli düzeltme: `contested` yeniden F5 condition-reference kökünde, resolved criterion'dan
bağımsız researcher-only alan olmalıdır. Rater/adjudication handling enum'larına girmemeli ve
disagreement'tan otomatik türememelidir.

## Karar

R2'nin amaçladığı iki düzeltme kabul edilebilir durumdadır; ancak bunları taşıyan kayıt yerleşimi
E2c için güvenli değildir. Önceki E1b teslimleri değiştirilmeden korunacaktır.
[E1b-R3 briefi](../../llm-benchmark-E1b-r3-task.md) yalnız katman ayrımı ve `contested` yerleşimiyle
sınırlandırılmıştır. E1b-R3 kabul edilmeden E1c/E2c başlamaz; Phase 7G/8 kapalıdır.

