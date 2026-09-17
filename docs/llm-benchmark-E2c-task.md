# E2c — Layer-B iki-rater referansları ve provenance

Durum: E1b insan onayı ile E2a/E2b kabulünü bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Onaylı E1b rubriğini koşul bazlı iki bağımsız insan referansı olarak kaydedebilen şema, araç ve validator desteği ekle. Bu görev hiçbir referans etiketi üretmez ve mevcut tek rating'i yeni rubriğe çeviremez.

## Kapsam

E1b kabulündeki kesin alanları oku. Değişiklik alanı: Phase 7G builder/schema, annotation/import araçları, validator, status/rollup ve ilgili testler. Blind/context sıralaması E2a/E2b sözleşmesini korur. `results/dataset_audit` yetkili dosyalarını worker çalıştırmasında yenileme.

## Davranış sözleşmesi

- Kabul edilen her A/B/C ve varsa D için rater_a/rater_b ayrı nominal action, clarification, harm, utility, applicability/handling, confidence/gerekçe ve rubrik sürümü taşır.
- Rater provenance kimlik, rol, zaman ve maruziyet beyanını açık taşır; rater B'ye A cevabı gösterilmez.
- Agreement ve adjudication ham görüşleri korur. `uncertain`, `contested`, `either_defensible`, missing ve N/A birbirinden ayrıdır.
- Layer A author expectation ve Layer C model output Layer B'yi dolduramaz. Import/export round-trip bu ayrımı korur.
- Eski şema açık legacy statüsüyle okunur veya açıklayıcı hata verir; tamamlanmış yeni referans gibi görünmez.

## Kabul ve teslim

Şema/validation testleri insan etiketi uydurmadan boşluk, provenance, version ve yasak Layer-A/C aktarımını sınamalı. Pozitif değerli rater fixture'ı gerekiyorsa AGENTS.md sınırı nedeniyle durup ana inceleyiciye tasarım sun; kendiliğinden üretme. `layer-b-contract.md`, migration/legacy notu ve standart kanıt paketini teslim et. E4 insan işini başlatma.

