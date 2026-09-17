# E1c-R2 — Resolved gözlem ve bağımsız endpoint paydası düzeltmesi

Durum: Hazır. Kök: `/home/kaan/AI_Search`. Yürütücü: E1c worker.  
Önkoşul: [E1c-R1 inceleme kararı](reviews/llm-benchmark/E1c-r1-acceptance.md).  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

E1c-R1'de kalan dört blokajı kapat: analiz birimini tek resolved yanıt kaydına bağla, contested
seçenek çelişkisini kaldır, error-asymmetry ölçümünü harm endpointinden ayır ve yardımcı oranların
paydalarını kapat. Mevcut doğrulanmış matematiği, logical-job kimliğini, CI seçeneklerini ve
`DRAFT / NOT EFFECTIVE` sınırını koru.

## Teslim kapsamı

Yeni teslim dizini `docs/reviews/llm-benchmark/E1c-r2/` olsun. Yalnız etkilenen amendment,
estimand contract, legacy delta, revision map ve standart kanıt paketini üret. Önceki teslimler,
frozen belgeler, stimulus, audit/QC, kod ve insan rating'leri değişmez.

## Zorunlu düzeltmeler

1. Her canonical logical response için en fazla bir `resolved_response_rating` label-of-record
   tanımla. Kaynağı rater uzlaşması veya tamamlanmış adjudication olsun. İki ham rater görüşü ayrı
   model gözlemleri değildir; unresolved kayıt F1/F3/F4 endpoint payına veya paydasına girmez.
2. E-act, E-harm, E-util ve yardımcı oranları resolved response tekrarları üzerinden hesapla.
   Üç provider tekrarı × iki rater, en fazla üç endpoint gözlemi üretir; altı üretmez.
3. `contested handling` durumunu koşulsuz exclusion listesinden çıkar. D-A ve D-B seçeneklerini
   ayrı göster; insan seçimi yapılmadan contested kayıtlar için etkin payda veya sonuç üretme.
4. Error-asymmetry için E-harm'dan bağımsız kapalı sözleşme yaz: uygun B/C çiftini, resolved
   koşul-uygunluk referansını, resolved yanıt eyleminden ikili violation türetimini ve discordant
   hücreleri tanımla. E1b handling etiketi ile frozen üçlü karar arasındaki mapping insan kararı
   bekliyorsa ölçümü pending tut; harm-uncertain seçeneğini bu paydada kullanma.
5. H-U1 uncertain rate ve H-T1b partial rate dahil her yardımcı/sensitivity oranı için payı,
   paydayı, dışlamaları ve sıfır payda çıktısını açık yaz.
6. `stratified_by_assistant_stance` içinde kategori × stance hücrelerinin korunduğunu belirt.
   AM özdeş stance ile DU/NH farklı stance ayrımını ve NB'nin veri-temelli mappingini göster;
   kategori ya da stance ekseninde örtük havuzlama yapma.

## Kabul

- Üç yanıt ve iki rater örneği en fazla üç resolved endpoint gözlemi verir.
- Unresolved ham görüşler endpoint değerine girmez.
- D-A/D-B seçilmeden contested sonuç veya exclusion kuralı etkinleşmez.
- Error-asymmetry kendi eligibility/payda sözleşmesine sahiptir ve unresolved mappingde pendingdir.
- Uncertain ve partial yardımcı oranlarının pay/payda ile zero-denominator davranışı nettir.
- Kategori × stance hücreleri izlenebilir ve havuzlanmamıştır.

Teslimden sonra dur; insan kararlarını `APPROVED` yapma ve E5/E6'ya etkin devir verme. Beklenen
ana teslim: `docs/reviews/llm-benchmark/E1c-r2/README.md`.
