# Phase 6B — Pilot sampling methodology

## Durum

Bu belge final seçim değil, seçimin güvenli biçimde yapılabilmesi için önceden tanımlanmış yöntemdir. `results/dataset_audit/sampling_report.json` şu anda `blocked_pending_methodology_and_license_approval` durumundadır. Final `dataset/pilot/manifest.json` oluşturulmamıştır.

50 original multi-turn örneği Phase 6B’de oluşturulmayacaktır.

## Birim analizi

- XSTest birimi: tek prompt.
- JBB-Behaviors birimi: behavior/goal/target kaydı.
- JBB `judge_comparison` birimi: attack prompt + target + judge labels; XSTest benign alt kümesiyle karışık.
- WildGuardTest birimi: prompt-response çifti veya prompt-only item; kaynak etiketleri üç ayrı görev içindir.

Bu birimler aynı “sample” kavramı gibi birleştirilemez. Her kayıt `source_unit_type` alanını taşımalı ve metrikler kaynak birimine göre ayrılmalıdır.

## Önerilen seçim planı

### XSTest — aday 100

Pinned CSV alındıktan sonra `label`, `type`, `focus` ve güvenli/unsafe kontrast yapısı üzerinden stratified sampling yapılır. 50 safe + 50 unsafe yalnızca bir aday dağılımdır; her type için gerçek uygunluk ve duplicate kontrolü tamamlanmadan kesinleştirilmez. Safe örnekler over-refusal, unsafe contrast örnekler refusal uygunluğu için ayrı analiz edilir.

### JBB — aday 100

İki metodolojik seçenek vardır:

1. `behaviors/harmful` içinden 100 behavior seçmek: Bu tam kapsamlı harmful-behavior/refusal benchmark olur, jailbreak benchmarkı olmaz.
2. JBB artifacts/judge-comparison içinden attack prompt seçmek: Attack method, target model, artifact revision, source overlap ve raw redistribution koşulları ayrıca onaylanmalıdır.

Bu karar verilmeden 100 JBB kaydı seçilmeyecek ve sonuçlar “jailbreak” diye raporlanmayacaktır.

### WildGuardMix — aday 50

Sadece immutable `wildguardtest/test` snapshotı, access/license/privacy review sonrasında adaydır. `adversarial`, prompt/response label availability, `subcategory` ve agreement alanlarıyla stratified sampling yapılır. Harmfulness ve refusal ayrı source label olarak korunur. Native ID yoksa türetilmiş locator politikası onaylanmadan seçim yapılmaz.

### Original multi-turn — 50

Phase 6B kapsamı dışındadır; sonraki onaylı fazda oluşturulacaktır.

## Duplicate ve overlap yöntemi

1. Source ID eşleşmesi.
2. Exact UTF-8 prompt/goal hash.
3. Unicode NFKC + casefold + whitespace collapse sonrası normalized hash.
4. Bilinen source relationship’leri rapora yazma.
5. Semantic near-duplicate bu fazda otomatik çıkarma için kullanılmaz; kullanılacaksa embedding/model/threshold ve false-positive audit ayrıca onaylanır.

Hiçbir örnek sessizce silinmez. Her dışlama `source_dataset`, `source_sample_id` veya locator, hash, gerekçe ve karar durumuyla audit raporuna yazılır.

## Reproducibility

Sampling seed config içinde sabitlenir. Source revision, source file hash, retrieval timestamp, inclusion/exclusion rules ve candidate pool hash manifest metadata’sına girer. Aynı snapshot ve seed olmadan aynı seçim garanti edilmez.

## Finalization gate

`scripts/build_pilot_manifest.py` şu koşullar sağlanmadan final manifest üretmez:

- tüm source revisionları immutable,
- source file hash’leri mevcut,
- row-level schema/label/source-ID validation başarılı,
- pairwise exact/normalized overlap tamamlanmış,
- JBB unit-of-analysis kararı verilmiş,
- WildGuard access, ODC-By ve responsible-use koşulları onaylanmış,
- raw/metadata-only redistribution kararı onaylanmış.
