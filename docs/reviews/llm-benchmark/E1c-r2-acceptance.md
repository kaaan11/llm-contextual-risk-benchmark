# E1c-R2 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1c-R2 KABUL EDİLMEDİ; E1 BİLİMSEL KARAR KAPISI AÇIK KALDI.**

## Doğrulanan düzeltmeler

[E1c-R2 briefi](../../llm-benchmark-E1c-r2-task.md) ile teslim karşılaştırıldı. Önceki dört
blokajın hedeflenen çekirdeği kapatılmıştır:

- Her canonical logical response en fazla bir `resolved_response_rating` üretir; iki ham rater
  görüşü iki model gözlemi sayılmaz ve unresolved kayıt endpointlere girmez.
- Contested davranışı koşulsuz exclusion listesinden çıkarılmış; D-A/D-B seçimi olmadan sonuç
  üretilmemiştir.
- Error-asymmetry E-harm'dan ayrılmış; eligibility, violation ve discordant-cell sözleşmesine
  bağlanmış, mapping kararı beklerken pending bırakılmıştır.
- Uncertain, partial, F3 gap ve F4 gap/NA yardımcı oranları için pay, payda ve sıfır-payda
  davranışı yazılmıştır.
- Kategori × assistant-stance hücreleri korunmuş; NB veri-temelli differing mappinginde tutulmuş
  ve örtük havuzlama yasaklanmıştır.

Altı komut kaydı ve log hedefleri, `run-outputs.sha256`, belge bağlantıları ve
`git diff --check` bağımsız doğrulandı. McNemar sonucu `1.862645149230957×10^-9`, KÖ-3 sonucu
`P(X≥6)=0.5281675158588918` olarak yeniden hesaplandı. Stimulus hash'i değişmedi; audit
geçmişleri 51 ve 5 satırla aynı hashlerde kaldı. Frozen dosya, kod, insan annotation'ı veya API
çağrısı değişikliği yoktur.

## Bloklayıcı eksik

### R1 — Global exclusion listesi endpoint kurallarıyla çelişiyor

`estimand-contract.md` §2, E-act için F3 gap'in F1 paydasını etkilemediğini ve F1 geçerliyse
gözlemin orana girdiğini korur. Buna karşılık §3'teki “Exclusion (kapalı liste)” `missing
criterion (F3 gap)` kaydını herhangi bir endpoint ayrımı yapmadan dışlar. Aynı response bu iki
kurala göre E-act'e hem girer hem girmez. E6a bu çelişkiyi bilimsel seçim yapmadan çözemez.

Exclusion sözleşmesi endpoint bazlı hale getirilmelidir. F3 gap, yalnız F3 gerektiren E-harm ve
error-asymmetry gibi ölçümlerin eligibility/paydasını etkiler; geçerli resolved F1'i E-act'ten
çıkarmaz. Benzer biçimde F4 gap/NA yalnız F4 gerektiren ölçümlerde uygulanmalıdır. Response
düzeyi yapısal/gate/unscorable durumları ile endpoint-alanı düzeyi eksiklikler iki ayrı listede
tanımlanmalı; her biri için ayrı sayı ve gerekçe korunmalıdır.

## Karar ve devam

Teslim önceki revizyonun amaçlarını karşılıyor, fakat tek kalan kapsam çelişkisi analiz nüfusunu
değiştirebilir. Ham E1c-R2 teslimi korunacaktır.
[E1c-R3 briefi](../../llm-benchmark-E1c-r3-task.md) yalnız endpoint-scope exclusion düzeltmesini
kapsar. E1c-R3 kabulü ve insan bilimsel kararları olmadan E1 kapanmaz; E5/E6 etkinleşmez.
