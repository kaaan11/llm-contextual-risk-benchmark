# E1b-R1 — Ana inceleyici kararı

Tarih: 2026-09-09. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1b-R1 KABUL EDİLMEDİ; E1c/E2c KİLİTLİ.**

## İnceleme sonucu

[E1b-R1 briefi](../../llm-benchmark-E1b-revision-task.md), worker README'si, revizyon haritası,
rubrik, şema, sınır örnekleri, karşılaştırmalar ve kanıt logları incelendi. İlk E1b kararındaki
şu eksikler giderilmiştir:

- Stable reviewer kimliği rol bilgisinden ayrılmış; aynı kimliğin iki slotta kullanımı yasaklanmış.
- `rater_a` ve `rater_b` ham kayıtları, agreement ve ayrı adjudication nesnesi tanımlanmış.
- Disagreement, `either_defensible` ve araştırmacı tarafından atanabilen `contested` ayrılmış.
- Explicit scoreability görüşü confidence alanından ayrılmış.
- F1–F4 operational outcome kapısının arkasına alınmış; execution sınıfları E5c'ye bırakılmış.
- Koşullu gerekçe alanları ve `DRAFT / NOT EFFECTIVE` sınırı düzeltilmiş.

Paket bağımsız olarak doğrulandı: `schema-draft.json` ve sekiz satırlık `commands.jsonl` parse
edildi; bütün komut kayıtları exit 0 ve mevcut log hedefleri taşıyor; `run-outputs.sha256` girdileri,
Markdown bağlantıları ve `git diff --check` geçti. Stimulus SHA-256 ile 51/5 satırlık append-only
audit geçmişleri kabul edilmiş referanslarla aynı. Kod, insan rating'i veya API çağrısı yoktur.

## Kalan blokajlar

### R1 — F3'ün kullanacağı çözülmüş criterion yok

F5 zarfındaki `criterion_id` koşul düzeyinde tek olsa da `allowed_assistance`,
`restricted_capability` ve `clarification_sufficiency` yalnız iki ham rater slotunun içinde
bulunuyor. Rater metinleri aynı olmak zorunda değil ve `agreement` yalnız bir enum. Agreement
halinde hangi üçlünün record-of-reference olduğu, disagreement halinde adjudication öncesi F3'ün
hangi metne bağlandığı ve çözülmüş criterion'ın provenance'ı tanımlanmıyor. Adjudication nesnesinde
bir üçlü bulunması bu boşluğu yalnız uyuşmazlık yolunda kısmen kapatıyor.

Bu nedenle `criterion_ref == condition_reference.criterion_id` yalnız doğru koşulu buluyor;
F3'ün kararını değerlendireceği tek, çözülmüş criterion sürümünü bulmuyor. E2c bunu kayıpsız ve
deterministik biçimde uygulayamaz.

Gerekli düzeltme: ham iki criterion önerisini koruyan, ayrıca yalnız iki insan görüşü tamamlandıktan
sonra oluşan bir `resolved_reference` tanımlanmalı. Bu nesne stable criterion ID/version, çözülmüş
üçlü, resolution source (`rater_agreement` veya `adjudication`) ve kaynak rater/adjudication
referanslarını taşımalı. F3 yalnız bu nesnenin kimliğine bağlanmalı; pending/disagreement veya
eksik resolved reference varken F3 yasak olmalı.

### R2 — `unscorable_content` frozen kurala ek şart getiriyor

Frozen annotation protocol §6.2, iki rater'ın ikisinin de açıkça `unscorable_content` işaretlemesini
yeterli kılar; yalnız tek rater'ın belirsizliği adjudication'a gider. R1 rubriği ve şeması ise iki
explicit unscorable görüşüne ek olarak adjudication onayı istiyor. Bu, mühürlü kurala yeni bir kapı
ekler ve worker yetkisinde değildir.

Gerekli düzeltme: iki explicit unscorable görüşü final `unscorable_content` üretmeli. Tek taraflı
unscorable/scoreable ayrılığı adjudication'a gitmeli. Confidence hiçbir durumda scoreability
üretmemeli. Frozen kural değiştirilmek isteniyorsa bu taslakta yapılamaz; resmi protokol eki ve
insan onayı gerekir.

## Karar ve devam

Revizyonun büyük bölümü başarılıdır, fakat kalan iki konu E2c'nin veri modelini ve frozen scoring
kapısını doğrudan etkiler. Ham E1b ve E1b-R1 teslimleri kanıt olarak değiştirilmeden korunacaktır.
[E1b-R2 briefi](../../llm-benchmark-E1b-r2-task.md) yalnız bu iki düzeltmeyle sınırlandırılmıştır.
E1b-R2 kabul edilmeden E1c veya E2c başlamaz; Phase 7G/8 kapalıdır.

