# E3a — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E3a KABUL EDİLMEDİ.**

## Doğrulanan güçlü yönler

[E3a briefi](../../llm-benchmark-E3a-task.md), Markdown/JSON envanteri ve kanıt paketi
incelendi. Teslim şu sınırları doğru korur:

- 50 item ve 171 condition kaydı kapsanır; örnekleme veya örnekten toplama tahmin yoktur.
- Final kullanıcı metni 50/50 item'da bayt-eşittir. 29 üç-koşullu ve 21 D-kollu item ayrımı
  `control_strategy` ile uyumludur.
- 19 satır `REVIEW` insan kuyruğu olarak sunulur; KEEP/REVISE/REJECT, metin düzeltmesi veya yeni
  stimulus sürümü üretilmez.
- Coherence, referent, risk ambiguity, D semantik ipucu, assistant stance ve byte/token sınırları
  birbirinden ayrılır. Tokenizer profili yokken token ihlali hükmü verilmez.
- DU004'ün leksik taramada negatif olması aklama olarak kullanılmaz; otomasyon sınırı açık tutulur.

Bağımsız sayımda exact B/C assistant eşliği 7, farklılık 43 ve D kolu 21 bulundu; teslimle
uyumludur. Verilen turn hashlerinin tümü stimulus metnine çözülür. 50 hedefli stimulus testi,
manifest checksumları, bağlantılar ve `git diff --check` geçti. Stimulus ve audit geçmişleri
değişmedi.

## Bloklayıcı eksikler

### R1 — Tarama kalıcı teslimden yeniden üretilemiyor

`commands.jsonl`, envanteri `python3 /tmp/opencode/e3a_scan.py` ile üretir; betik teslim dizininde
ve manifestoda yoktur. `/tmp` kalıcı kanıt değildir. Markdown yöntem tablosu tokenization,
stopword listesi, document-frequency evreni, tie ordering ve JSON üretim ayrıntılarını tamamen
tanımlamadığı için 19 aday ile ölçüm tablosu yalnız kalıcı artefaktlardan yeniden üretilemez.

Tarama helper'ı teslim altına alınmalı. Salt-okunur stimulus girdisi ve ayrı output yolu kabul
etmeli; `/tmp` çıktısına yeniden üretim yapılıp teslim JSON'u ile byte veya canonical-JSON eşliği
doğrulanmalıdır. Komut kaydı yalnız teslimdeki kalıcı helper'a referans vermelidir.

### R2 — Altı R-REF bulgusu konum/hash sözleşmesini ihlal ediyor

Brief, doğrudan alıntıyı çoğaltmadan konum ve hash ister. R-REF1 bulgularının altısında
`location.text_sha256` yoktur; buna karşılık `evidence` alanı prompttan kısa ifadeleri doğrudan
kopyalar. README'nin “JSON'da tam hash” iddiası bu altı satır için yanlıştır.

Her R-REF bulgusu turn ID ve tam metin SHA-256 taşımalı; Markdown ve JSON kanıt alanlarından
doğrudan prompt parçası çıkarılmalıdır. İnsan inceleyici frozen kaynağı turn ID/hash üzerinden
bulmalıdır.

### R3 — Ham regex eşleşmesi referent hükmüne dönüştürülmüş

R-REF1 kuralı yalnız `this|these` ardından dört karakterli token arar. Buna rağmen evidence,
her eşleşmede “referent resolved only via context” der. `this behave` ve `this before` örnekleri
bizzat teslimde fiil/zarf olabileceği belirtilen ham eşleşmelerdir; otomasyon bunlarda referent
varlığını veya context ile çözüldüğünü göstermemiştir. Bu ifade otomatik aday üretimini insan
discourse kararına dönüştürür.

Kanıt yalnız regex eşleştiğini söylemeli. Noun phrase olup olmadığı, bir referent bulunup
bulunmadığı, referentin bağlam gerektirip gerektirmediği ve risk ambiguity ilişkisi ayrı insan
karar alanları olarak açık kalmalıdır.

## Karar ve devam

Envanterin yapısal sayımları güçlüdür, ancak bulgu provenance'ı ve tekrar üretilebilirliği kabul
için tamamlanmalıdır. Ham E3a teslimi korunacaktır.
[E3a-R1 briefi](../../llm-benchmark-E3a-r1-task.md) yalnız R1–R3 düzeltmeleriyle sınırlıdır.
