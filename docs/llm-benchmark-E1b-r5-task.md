# E1b-R5 — Layer-C slot şeması referans bütünlüğü

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1b worker.  
Önkoşul: [E1b-R4 inceleme kararı](reviews/llm-benchmark/E1b-r4-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

R4'ün koşullu presence mantığını değiştirmeden, dalların kullandığı bütün Layer-C slot alanlarını
aynı şema scope'unda tanımla. Bu yalnız schema-ref bütünlüğü düzeltmesidir; taxonomy, bilimsel
kurallar, katmanlar, adjudication akışı veya applicability kararları yeniden tasarlanmaz.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1b-r5/` olsun. Düzeltilmiş şema, kısa rubrik/ref
notu, revision map ve standart kanıt paketini üret. Önceki teslimler, kod, frozen dosyalar,
stimulus, audit/QC ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. `RESPONSE_RATING.structure.slot_schema` içinde F1, F2, F3, F4, `unscorable_reason`,
   `f3_gap`, `f4_gap` ve `applicability_resolution` alanlarını açıkça tanımla. Presence'ı
   koşulsuz `required` bayrağıyla verme; R4 `presence_branches` yönetsin.
2. F1–F4 nested tanımları üst düzey F1–F4 enum/nesne sözleşmelerine açık ref ile bağlansın.
   F3 `criterion_ref` ID/version ve rationale; F4 value/rationale ile koşullu
   `inapplicability_reason` şeklini kayıpsız taşısın.
3. `f3_gap` yalnız `not_scored_missing_criterion` değerini kabul etsin ve resolved ref yokluğu
   dışında yasak olsun.
4. `f4_gap` açık applicability reason taşısın. `applicability_resolution`, conditional hücreyi
   boolean applies + zorunlu reason ile çözsün; conditional olmayan hücrelerde yasak olsun.
5. Adjudication final dallarında kullanılan final F1–F4/reason/gap/resolution alanları da aynı
   scope'ta tanımlı olsun veya açık, çözülebilir schema ref kullansın.
6. Şema kontrolü, presence ve adjudication dallarında adı geçen her alanın bulunduğu scope'ta
   tanımlı olduğunu hesaplayarak doğrulasın; yalnız metinde anahtar araması yapmasın.

## Kabul örnekleri

- Schema-ref linter hiçbir undeclared branch field bulmaz.
- Unscorable ve scoreable dal kuralları R4 ile aynı kalır.
- F3/F4 gap ve applicability alanları yanlış dallarda reddedilir.
- Nested F1–F4 enum/değer sözleşmeleri üst düzey tanımlarla drift edemez.
- R2/R3 kuralları için regresyon kontrolleri geçer; insan etiketi üretilmez.

## Doğrulama ve durma

JSON parse ve gerçek alan-ref çözümleme kontrolünü; R4 presence dalları, adjudication finali,
layer/timing, frozen §6.2, resolved criterion ve contested regresyon kontrolleriyle birlikte çalıştır.
Standart checksum/link/frozen/audit kanıtlarını bırak. Teslimden sonra dur ve yeniden inceleme bekle.

