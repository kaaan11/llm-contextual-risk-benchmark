# E1b-R5 — Rubrik/ref notu (kısa)

**Statü: DRAFT / NOT EFFECTIVE.** Bu not, R4 rubrik metnini (`../E1b-r4/rubric-draft.md` §8P)
değiştirmez; yalnız şema-scope beyanını ekler. Bilimsel dal mantığı (Dal U/S, final dalları,
gap kuralları) R4 ile aynıdır.

## Ne değişti (yalnız şema)

1. `RESPONSE_RATING.structure.slot_schema` artık dalların kullandığı 8 alanı açıkça tanımlar:
   F1, F2, F3, F4, `unscorable_reason`, `f3_gap`, `f4_gap`, `applicability_resolution`
   (+ `inapplicability_reason`, conditional F4 nedeni olarak).
2. Presence, hiçbir alanda koşulsuz `required` bayrağıyla verilmez; tek otorite
   `presence_branches`'tır (slot tanımlarındaki `presence` notları dallara işaret eder).
3. Nested F1–F4, üst düzey `#/fields/F1`–`#/fields/F4` sözleşmelerine `ref` ile bağlıdır ve
   enum/değer/requires şeklini kayıpsız taşır (drift, ref-çözümleme kontrolüyle denetlenir).
4. `f3_gap` yalnız `not_scored_missing_criterion` değerini alır; resolved yokluğu dışında yasaktır.
5. `f4_gap` applicability reason taşır; `applicability_resolution` conditional hücreyi boolean
   applies + zorunlu reason ile çözer; conditional olmayan hücrelerde yasaktır.
6. Adjudication final dallarındaki final F1–F4/reason/gap/resolution alanları
   `final_field_scope` ile aynı scope'un slot tanımlarına çözülür
   (`final_fields` listeleri dallarda açık yazılıdır).

## Ne değişmedi

Dal mantığı, enum'lar, katman/zaman, kimlik kuralları, resolved akışı, contested yerleşimi,
§6.2 davranışı, yasaklar (6 yeni yasak R4'ten aynen durur), uygulanabilirlik gövdesi,
sınır örnekleri (B-7U geçerli; yeni örnek gerekmedi).
