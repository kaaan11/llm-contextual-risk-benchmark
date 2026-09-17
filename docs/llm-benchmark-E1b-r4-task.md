# E1b-R4 — Layer-C koşullu alan sözleşmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1b worker.  
Önkoşul: [E1b-R3 inceleme kararı](reviews/llm-benchmark/E1b-r3-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

Layer-C response-rating zarfındaki scoreability ile F1–F4 presence kurallarını çelişkisiz ve
makinece uygulanabilir hale getir. R3 katman ayrımını, contested yerleşimini, R2 resolved
criterion akışını ve frozen §6.2 davranışını değiştirme.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1b-r4/` olsun. Düzeltilmiş rubrik, şema, yalnız
etkilenen sınır örnekleri, revision map ve standart kanıt paketini üret. Önceki kanıtlar, üretim
kodu, frozen dosyalar, stimulus, audit/QC ve insan rating'leri değişmez.

## Zorunlu kurallar

1. Layer-C ham slot için açık bir discriminated/conditional sözleşme tanımla:
   - `scoreable_view=unscorable_content`: `unscorable_reason` zorunlu; F1–F4 yasak.
   - `scoreable_view=scoreable`: `unscorable_reason` yasak; F1 ve F2 zorunlu.
2. Scoreable dalında F3 yalnız aynı koşulun resolved criterion ID/version'ı mevcutsa zorunlu
   olsun. Yoksa F3 yasak ve açık `not_scored_missing_criterion` durumu taşınsın; tahminî
   `absent/uncertain` üretilmesin.
3. Scoreable dalında F4 applicability=`applies/conditional-resolved-to-applies` ise zorunlu;
   `not_applies` ise F4 alanı yasak ve ayrı applicability nedeni korunur.
4. Tek taraflı unscorable disagreement adjudication'ında final `scoreable_view` açıkça yazılsın.
   Final scoreable ise final F1–F4 aynı presence kurallarına uysun; final unscorable ise F1–F4
   yasak olsun. Adjudication ham slotları değiştirmesin.
5. İki explicit unscorable doğrudan final davranışı ile operational non-scorable outcome'da hiç
   rating zarfı oluşturmama kuralını koru.
6. Gerçek veya sentetik rater etiketi üretme; yalnız şema ve soyut geçiş kontrolleri kullan.

## Kabul örnekleri

- Unscorable slot + F1 veya F2 reddedilir; unscorable reason eksikse reddedilir.
- Scoreable slotta F1/F2 eksikse reddedilir; unscorable reason varsa reddedilir.
- Resolved criterion yokken F3 değeri reddedilir ve gap durumu korunur.
- NH/not-applicable utility satırında F4 değeri reddedilir; uygulanabilir koşulda eksik F4
  reddedilir.
- Tek taraflı disagreement sonrası adjudicated-unscorable finalinde F1–F4 bulunmaz; ham scoreable
  ve unscorable slotlar değişmeden kalır.

## Doğrulama ve durma

JSON parse, koşullu presence matrisi, adjudication final dalları, layer/timing, frozen §6.2,
resolved ref ve contested regresyon kontrollerini etiketsiz yapısal assertionlarla çalıştır.
Standart checksum/link/frozen/audit kanıtlarını bırak. Teslimden sonra dur ve yeniden inceleme bekle.

