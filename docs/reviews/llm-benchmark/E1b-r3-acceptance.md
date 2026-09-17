# E1b-R3 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E1b-R3 KABUL EDİLMEDİ; E1c/E2c KİLİTLİ.**

## Doğrulanan düzeltmeler

[E1b-R3 briefindeki](../../llm-benchmark-E1b-r3-task.md) iki yerleşim hedefi karşılanmıştır:

- Layer-B F5 slotlarından response scoreability ve F1–F4 çıkarılmış; ayrı Layer-C,
  post-evaluation `response_rating` zarfı eklenmiştir.
- `contested`, resolved criterion dışına ve F5 köküne taşınmıştır; researcher-only niteliği,
  enum ayrımı ve disagreement'tan türememe kuralı korunmuştur.
- R2'nin resolved criterion ID/version bağı ve frozen §6.2 geçişleri korunmuştur.

Teslim bağımsız doğrulamada parse edildi. Sekiz komut kaydı exit 0'dır; log hedefleri,
checksumlar, bağlantılar ve `git diff --check` geçmiştir. Önceki paket manifestlerinin kapsadığı
dosyalar mevcut hashleriyle eşleşmektedir. Stimulus ve append-only audit geçmişleri değişmemiştir.

Worker, R3 sırasında E1b-R2'nin iki log adımını yanlışlıkla yeniden çalıştırıp sonra onardığını
README'de açıklamıştır. Mevcut E1b-R2 manifestosu geçmektedir; ancak `commands.jsonl` kendi
manifestosunda hashlenmediğinden olay öncesi bayt kimliği bağımsız olarak kanıtlanamaz. Bu olay
bilimsel veri veya frozen artefaktı etkilememiştir.

## Kalan blokaj — Unscorable slot yine skor alanı gerektiriyor

Layer-C `response_rating.slot_schema` içinde F1 ve F2 `required=true` olarak koşulsuzdur.
`scoreable_view=unscorable_content` olduğunda da aynı slot bu alanları zorunlu tutar. Frozen §6.2
ise rubriğin uygulanamadığı response için disposition üretilmemesini gerektirir. Böylece şema aynı
ham görüşten hem “unscorable” hem disposition/clarification skoru istemektedir.

F3/F4 nesnelerinin slotta ne zaman bulunacağı da açık bir koşullu-presence kuralına bağlı değildir;
özellikle F3 resolved criterion yokken yasak, F4 ise NH'de uygulanamaz olmalıdır. Üst seviye metin
bu durumları tarif etse de Layer-C zarf sözleşmesi bunları makinece ayırmıyor.

Gerekli düzeltme:

- `scoreable_view=unscorable_content`: `unscorable_reason` zorunlu; F1–F4 alanlarının tamamı yasak.
- `scoreable_view=scoreable`: F1 ve F2 zorunlu; F3 yalnız resolved criterion mevcutsa zorunlu,
  yoksa alan yasak ve açık `not_scored_missing_criterion`; F4 yalnız applicability izin veriyorsa
  zorunlu, aksi halde alan yasak.
- Tek taraflı unscorable adjudication nesnesi final scoreability'yi ve buna bağlı final F1–F4
  alanlarının presence kurallarını aynı şekilde uygulamalı; ham slotlar korunmalı.

## Karar

R3 yerleşim düzeltmeleri kabul edilebilir durumdadır; kalan sorun Layer-C koşullu alan
sözleşmesidir. [E1b-R4 briefi](../../llm-benchmark-E1b-r4-task.md) yalnız bu son çelişkiyle
sınırlandırılmıştır. E1b-R4 kabul edilmeden E1c/E2c başlamaz; Phase 7G/8 kapalıdır.

