# E3a-R2 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **ACCEPTED. E3a ENVANTER ZİNCİRİ KABUL EDİLDİ.**

## Kabul edilen kapsam

[E3a-R2 briefindeki](../../llm-benchmark-E3a-r2-task.md) iki blokaj kapatılmıştır.

- `assistant_shared_bc`, B ve C koşullarındaki assistant turn dizilerini sıra, rol ve UTF-8
  metin baytlarıyla exact karşılaştırır. Normalize token kümeleri yalnız ayrı betimleyici
  `assistant_jaccard_bc` ölçümünde kullanılır.
- Exact sayım 7 shared ve 43 differing sonucunu verir; shared kayıtların yedisi de AM'dir.
  Token kümeleri aynı, metin sırası farklı yapısal örnekte exact sonuç `False`, Jaccard uzaklığı
  `0.0` çıkarak iki ölçümün ayrımı doğrulanmıştır.
- Helper output ile input aynı resolve olduğunda reddeder. Repo içinde yalnız
  `docs/reviews/llm-benchmark/E3a-r2/stimulus-issues.json` allowlisttedir; diğer repo hedefleri
  `resolve()` sonrasında ve herhangi bir yazımdan önce reddedilir. Repo dışı geçici çıktı açıktır.
- R-REF 6/6 hash provenance'ı, dört açık insan kararı, 19 REVIEW adayı, karar-değil dili ve
  tokenizer profili olmadan token hükmü vermeme sınırı korunmuştur.

Bu kabul 19 adayın kusur, REVISE veya REJECT olduğu anlamına gelmez. E3b kararları gerçek insan
araştırmacıya aittir; stimulus v1 üzerinde değişiklik yetkisi vermez.

## Bağımsız kanıt

- Kalıcı helper repo dışı geçici dosyada çalıştırıldı; çıktı teslim JSON'u ile byte-eşittir.
- Stimulus inputu, üç mühürlü protokol belgesi, hedefli test dosyası ve helper'ın kendisi output
  olarak ayrı ayrı denendi; altı hedef de non-zero ret verdi ve hashleri değişmedi.
- Exact 7/43 sayımı ve exact/Jaccard divergence örneği bağımsız tekrarlandı.
- 50 hedefli stimulus testi, `run-outputs.sha256`, belge bağlantıları ve `git diff --check` geçti.
- Stimulus SHA-256 değeri `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`
  olarak kaldı. Audit geçmişleri 51 ve 5 satırla `e145afed…` ve `23755e0f…` hashlerinde kaldı.

## Karar ve sonraki kapı

E3a-R2 için yeni worker revizyonu gerekmiyor. E2b insan-onaylı E1 alan sözleşmesini; E3b ise
19 aday için araştırmacı kararını ve değişiklik gerekirse açık frozen-protokol yetkisini bekler.
Bu nedenle şu anda otomatik başlatılabilecek sıradaki worker paketi yoktur; aktif adım insan
bilimsel karar kapısıdır.
