# E1c-R1 — Estimand paydası ve analiz kimliği düzeltmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1c worker.  
Önkoşul: [E1c inceleme kararı](reviews/llm-benchmark/E1c-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E1c'deki beş blokajı kapatıp E6a'nın bilimsel seçim icat etmeden uygulayabileceği kapalı bir
taslak üret. Nominal, madde-eşit yaklaşımı; legacy ayrımını; karşıörnekleri ve
`DRAFT / NOT EFFECTIVE` sınırını koru.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1c-r1/` olsun. Düzeltilmiş estimand contract,
amendment delta, yalnız etkilenen legacy satırları, revision map ve standart kanıt paketini üret.
Önceki E1c kanıtı, frozen belgeler, stimulus, audit/QC, kod ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. E-act, E-harm ve E-util için kapalı pay/payda tablosu yaz. Her biri için madde-içi oranı,
   madde-eşit toplulaştırmayı ve `uncertain`, `partial`, `not_completed`, `not_applicable`,
   unscorable/missing, F3 gap, F4 gap/conditional applicability durumlarının davranışını göster.
   İnsan seçimi gereken alternatifleri onaysız tek kurala dönüştürme.
2. Duplicate/logical-job kimliğini protocol/data version + run ID + requested model identity +
   item + condition + repetition/seed boyutlarıyla tanımla veya E5a'nın canonical job ID'sine
   normatif ref ver. Provider attempt/retry yeni gözlem değildir; model/run değişimi duplicate
   değildir. E5a/E5c alan adları değişirse sözleşme anlamı korunmalıdır.
3. `stratified_by_assistant_stance` zorunlu çıktı eksenini ekle. AM özdeş assistant stance ile
   DU/NH farklı stance ayrı strata olmalı; kategori (DU/AM/NB/NH) ayrı eksen olarak kalmalı.
   Strata havuzlanmamalı ve zero-denominator açık raporlanmalı.
4. Eşleşmiş madde-eşit farklar için yöntem kararı verilmeden `exact CI` vaadini kaldır. CI
   seçeneklerini varsayım, küçük-n yasağı ve kullanım alanıyla sun; Clopper–Pearson'ı yalnız
   tek-oran çıktılarla sınırla. İnsan kararı ve freeze öncesi yöntem etkinleşmesin.
5. `either_defensible`/`contested` denominator davranışını D-A/D-B seçenek tablosu olarak tut.
   Seçim yapılmadan exclusion/payda kuralı uygulanmış gibi yazma. Unresolved disagreement ve
   eksik Layer-B referansının skor üretmemesi ayrı teknik kapı olarak kalabilir.
6. KÖ-3 kurulumunda 16 D'siz + 14 D'li ayrımını ve `.25/.125` olasılıklarını açık yaz; beklenen
   5.75 ve `P(X≥6)=0.5281675` bağımsız deterministik hesapla doğrulansın. KÖ-1 değeri de yeniden
   hesaplanmalı; rapordan kopyalanmış sayı olarak bırakılmamalı.

## Kabul

- Her endpoint için tüm E1b nominal/gap/applicability durumları tek anlamlı payda davranışına veya
  açık insan-kararı seçeneğine sahiptir.
- İki model/iki run kaydı duplicate sayılmaz; aynı canonical logical job'ın retry'si yeni gözlem
  sayılmaz.
- Assistant-stance strata zorunlu, kategori ekseninden ayrı ve havuzlanmamıştır.
- TBD CI yöntemi exact diye sunulmaz; CP'nin kapsamı doğru kalır.
- Onaysız D-A/D-B davranışı etkin kural gibi kullanılmaz.
- Matematiksel kontroller insan anotasyonu üretmeden geçer.

Teslimden sonra dur; insan kararlarını `APPROVED` yapma ve E5/E6'ya etkin devir verme.

