# E1b-R6 — Ref notu (kısa)

**Statü: DRAFT / NOT EFFECTIVE.** Bu not, R4/R5 dal mantığını ve R2/R3 kurallarını değiştirmez;
yalnız ref mekanizmasını açıklar. Bilimsel kural veya alan eklenmedi.

## Ne değişti (yalnız ref mekanizması)

1. Değer/requires şekillerinin tek canonical otoritesi `$defs`'tir (`F1–F4`,
   `unscorable_reason`, `f3_gap`, `f4_gap`, `applicability_resolution`,
   `inapplicability_reason` — her biri `def_id` + `def_kind` taşır).
2. `fields` dizisindeki F1–F4 girdileri placement metadata + `$ref` işaretçisidir; değer şekli
   taşımaz. Slot ve final girdileri `$ref` + presence notudur; değer şekli taşımaz.
   `$defs` dışı şekil kopyası drift ihlalidir (`no_duplicate_shape_outside_defs`).
3. Adjudication finali `final_payload_schema` ile kapalı şemadır: `final_scoreable_view`
   discriminator'ı `final_unscorable` / `final_scoreable` dallarını ayırır; final alanları
   `$defs` hedeflerine `$ref` ile bağlanır. Serbest metin `final_field_scope` kaldırıldı.
4. Linter her `$ref`'i belge kökünden token-token traverse eder (RFC 6901 `~0`/`~1` çözme dahil),
   hedefin `def_id`/`def_kind` değerini doğrular. `#/fields/F1` gibi dizi-içi geçersiz pointer
   reddedilir.

## Ne değişmedi

Dal mantığı, enum'lar, katman/zaman, kimlik, resolved akışı, contested yerleşimi, §6.2,
yasaklar (2 yeni yasak eklendi: `no_unresolvable_ref`, `no_duplicate_shape_outside_defs`),
uygulanabilirlik gövdesi, sınır örnekleri (B-7U geçerli; yeni örnek gerekmedi).
