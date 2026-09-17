# E1b-R5 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1b-R5 KABUL EDİLMEDİ; E1c/E2c KİLİTLİ.**

## Doğrulanan düzeltmeler

[E1b-R5 briefindeki](../../llm-benchmark-E1b-r5-task.md) sekiz Layer-C alanı artık
`slot_schema` içinde açık type/value ve presence tanımlarına sahiptir. R4 dalları, R3 katman
ayrımı, R2 resolved criterion akışı, contested yerleşimi ve frozen §6.2 davranışı korunmuştur.
Gap ve applicability nesnelerinin temel şekilleri de tanımlanmıştır.

Teslim JSON/JSONL, sekiz exit-0 komut kaydı, log hedefleri, checksumlar, bağlantılar ve
`git diff --check` açısından bağımsız kontrolden geçmiştir. Stimulus ve append-only audit
geçmişleri değişmemiştir.

## Blokaj — `$ref` değerleri çözülemiyor ve linter bunu sınamıyor

Nested F1–F4 alanları `#/fields/F1` … `#/fields/F4` referanslarını kullanır. `fields` bir JSON
dizisidir; standart JSON Pointer'da bundan sonraki token `0`, `1` gibi dizi indeksi olmalıdır.
Bağımsız pointer çözümleyici dört referansın tamamında `ValueError` üretmiştir. Dolayısıyla bu
referanslar üst düzey sözleşmelere bağlanmaz ve drift engellenmez.

Worker'ın “real ref resolution” kontrolü pointer'ı belge içinde izlemiyor. Yalnız ref stringini
beklenen literal ile karşılaştırıyor ve ayrıca `top = {field.id: field}` sözlüğünde değerleri
karşılaştırıyor. Bu, içerik eşitliğinin bazı parçalarını ölçer; referansın çözülebilirliğini
kanıtlamaz. README'deki `undeclared=[]` sonucu yalnız branch alan adlarının `slot_schema`
anahtarlarında bulunduğunu gösterir.

Adjudication `final_field_scope` da serbest metindir; `final_fields` adlarının slot scope'unda
bulunması kontrol edilir, fakat final payload'ın discriminator ve alan şekli gerçek bir nested
schema/ref olarak tanımlanmaz. E2c hâlâ kendi sözleşmesini icat etmek zorunda kalır.

## Gerekli düzeltme

Alan tanımlarını adreslenebilir bir map/`$defs` altında tutup nested F1–F4 ve adjudication final
dallarını gerçek, çözülebilir referanslara bağla. Linter her pointer'ı belge içinde traverse etmeli,
hedefin beklenen field ID/type olduğunu doğrulamalı ve bozuk pointer içeren yalıtılmış negatif
varyantı reddetmelidir. Koşullu dal mantığı değişmemelidir.

## Karar

R5 alan deklarasyonu sorununu kapatmıştır; ref bütünlüğü iddiası çürütülmüştür.
[E1b-R6 briefi](../../llm-benchmark-E1b-r6-task.md) yalnız gerçek ref çözümleme ve adjudication
final şemasına odaklanır. E1b-R6 kabul edilmeden E1c/E2c başlamaz; Phase 7G/8 kapalıdır.

