# E4a — Gerçek insan Phase 7G oturumları

Durum: **İNSAN İŞİ; WORKER'A ATANMAZ.**  
Önkoşul: E1 bilimsel kararları onaylı, E2 araçları kabul edilmiş, E3 maddeleri için uygulanabilir karar/sürüm hazır. Üst plan: [E4](llm-benchmark-assessment-and-plan.md).

## Amaç

İki bağımsız gerçek insan rater ile isolated-prompt değerlendirmelerini, gerekli adjudication'ı, ardından context incelemesi ve onaylı koşul referanslarını tamamlamak. Ajan annotation, gerekçe, adjudication veya insan kimliği üretmez.

## İnsan yürütme kontrolü

1. Rater kimlikleri, roller, rubrik sürümü, eğitim materyali ve önceki stimulus/expected-label/model-output maruziyet beyanı gerçek insanlarca kaydedilir.
2. Rater A ve B birbirinin yanıtını görmeden isolated oturumu tamamlar. Rater B bağımsız başka insandır.
3. İki rating tamamlanmadan context açılmaz. Uyuşmazlık varsa gerçek adjudicator gerekçe kaydeder.
4. Frozen gate `FAIL` ise madde KEEP olmaz. Context B/C/D ve Layer-B alanları onaylı sözleşmeye göre doldurulur.
5. Mevcut tek tarihsel rating'in kullanılabilirliği araştırmacı tarafından karara bağlanır; silinmez veya yeni rubriğe otomatik çevrilmez.

## Kanıt ve devir

Araçların kendi append-only ve snapshot davranışı kullanılır. `docs/reviews/llm-benchmark/E4a/README.md` yalnız oturum sayıları, kullanılan sürüm/hash, validator sonucu ve hassas olmayan provenance özeti taşır; blind key veya annotation içeriğini çoğaltmaz. Tamamlanınca ana inceleyici iki-rater, gate, ordering ve referans tamlığını salt okunur doğrular. E4b insan kararından önce Phase 8 başlamaz.

