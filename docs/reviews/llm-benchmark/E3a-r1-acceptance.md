# E3a-R1 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E3a-R1 KABUL EDİLMEDİ.**

## Doğrulanan düzeltmeler

[E3a-R1 briefindeki](../../llm-benchmark-E3a-r1-task.md) üç ana düzeltmenin çekirdeği
karşılanmıştır:

- Tarama helper'ı kalıcı teslim altında bulunur, parametrik input/output alır ve aynı stimulus
  girdisinden teslim JSON'u ile bayt-eşit geçici çıktı üretir.
- Altı R-REF1 bulgusunun tamamı canonical A turn ID ve frozen metinden çözülen tam SHA-256 taşır.
- R-REF kanıtlarından prompt parçaları çıkarılmış; noun phrase, referent varlığı, context ihtiyacı
  ve risk ambiguity ilişkisi dört ayrı açık insan kararı olarak tutulmuştur.
- R-REF2 kaynak turn hashleri eklenmiş; 19 aday REVIEW kuyruğu olarak kalmış ve otomatik
  naturalness/safety veya E3b kararı üretilmemiştir.

Bağımsız yeniden üretim byte-equal geçti. Mevcut korpusta exact B/C assistant eşliği de teslimdeki
alanla aynı sonucu verir: 7 shared, 43 differing. 50 hedefli stimulus testi, manifest checksumları,
bağlantılar ve `git diff --check` geçti. Stimulus ve audit geçmişleri değişmedi.

## Bloklayıcı eksikler

### R1 — `assistant_shared_bc` exact eşlik yerine token-kümesi eşliği kullanıyor

Brief, 7/43 **exact assistant eşliğinin** yeniden hesaplanmasını ister. Helper ise B/C assistant
metinlerini normalize edip stopword çıkarılmış token kümelerine dönüştürüyor ve
`assistant_shared_bc = (sa == sc)` hesaplıyor. Kelime sırası, tekrarlar, noktalama, büyük/küçük
harf ve stopword farkları bu alanda kaybolur. Mevcut dataset'te iki yöntem tesadüfen aynı 7/43
sonucunu veriyor; buna rağmen alanın algoritması ve adı farklı sözleşmeleri ifade eder.

`assistant_shared_bc`, B ve C'deki assistant turn dizilerinin rol/sıra/metin baytları üzerinden
exact karşılaştırması olmalıdır. Jaccard ölçümü ayrı betimleyici alan olarak kalabilir. Yeniden
üretilen JSON ve yöntem belgesi bu ayrımı açıkça göstermelidir.

### R2 — Output koruması mühürlü `docs/` yollarını korumuyor

Helper'ın `refuse_protected_output` fonksiyonu yalnız `dataset/` ve `results/` öneklerini
reddeder. Yan etkisiz kontrolde `docs/phase7e_preregistration.md` output yolu hiçbir hata
üretmeden kabul edildi; helper çalıştırılsaydı mühürlü protokol dosyasını JSON ile ezebilirdi.
Ayrıca output ile input yolunun aynı olması genel olarak reddedilmiyor. Bu, helper'ın
“frozen girdiye veya varsayılan repo verisine yazmaz” sözleşmesini karşılamaz.

Output hedefi input ile aynıysa daima reddedilmelidir. Repo içinde yalnız bu revizyon tesliminin
açıkça izin verilen `stimulus-issues.json` hedefi yazılabilir; repo dışındaki caller-owned geçici
çıktılar serbest kalabilir. Diğer tüm repo yolları, özellikle frozen `docs/`, dataset, results,
content, test ve helper dosyaları fail-closed reddedilmelidir.

## Karar ve devam

Bilimsel aday dili ve provenance artık yeterlidir; kalan iki konu helper sözleşmesi ve yazım
güvenliğidir. Ham E3a-R1 teslimi korunacaktır.
[E3a-R2 briefi](../../llm-benchmark-E3a-r2-task.md) yalnız bu iki düzeltmeyle sınırlıdır.
