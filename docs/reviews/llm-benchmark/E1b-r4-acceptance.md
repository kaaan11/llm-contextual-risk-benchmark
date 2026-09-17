# E1b-R4 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1b-R4 KABUL EDİLMEDİ; E1c/E2c KİLİTLİ.**

## Doğrulanan düzeltme

[E1b-R4 briefindeki](../../llm-benchmark-E1b-r4-task.md) koşullu presence mantığı doğru
kurulmuştur:

- Unscorable dalında reason zorunlu, F1–F4 yasaktır.
- Scoreable dalında F1/F2 zorunlu; F3 resolved criterion'a, F4 applicability'ye bağlıdır.
- Adjudication final scoreability'yi açık taşır ve ham slotları değiştirmez.
- Katman ayrımı, contested kökü, resolved criterion ve frozen §6.2 kuralları korunmuştur.

Teslim JSON/JSONL parse, sekiz exit-0 komut kaydı, log hedefleri, checksumlar, bağlantılar ve
`git diff --check` açısından bağımsız doğrulamadan geçmiştir. Stimulus ve append-only audit
geçmişleri değişmemiştir.

## Kalan blokaj — Presence dalları tanımsız slot alanlarına başvuruyor

R4, önceki `RESPONSE_RATING.structure.slot_schema` içinden F1–F4 tanımlarını kaldırmıştır.
Presence dalları ise F1, F2, F3, F4, `unscorable_reason`, `f3_gap`, `f4_gap` ve
`applicability_resolution` alanlarına başvurur. Bu sekiz alanın hiçbiri slot şemasında type/value
tanımına sahip değildir. Bağımsız ref kontrolü sekizini de “referenced but undeclared” bulmuştur.

Üst düzey F1–F4 tanımları semantiği açıklar, fakat nested slot içindeki alan şekli, gap nesneleri
ve applicability resolution yapısı için kapalı bir sözleşme oluşturmaz. E2c'nin validator'ı alan
tiplerini ve ek alan yasağını tahmin etmek zorunda kalır.

Gerekli düzeltme: sekiz alan slot şemasında açıkça tanımlanmalı; varlıkları `required=true` ile
değil yalnız `presence_branches` ile yönetilmelidir. F1–F4 üst düzey tanımlara referans vermeli;
gap ve resolution nesneleri enum/type/reason alanlarını açık taşımalıdır. Bir schema-ref linter,
presence/adjudication dallarında kullanılan her alanın aynı scope'ta tanımlı olduğunu doğrulamalıdır.

## Karar

R4'ün bilimsel dal mantığı kabul edilebilir durumdadır; kalan hata yalnız şema referans
bütünlüğüdür. [E1b-R5 briefi](../../llm-benchmark-E1b-r5-task.md) bu tek düzeltmeyle sınırlıdır.
E1b-R5 kabul edilmeden E1c/E2c başlamaz; Phase 7G/8 kapalıdır.

