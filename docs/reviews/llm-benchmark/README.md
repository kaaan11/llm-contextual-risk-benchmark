# LLM Benchmark — İnceleme ve kanıt düzeni

Bu dizin [worker briefleri](../../llm-benchmark-worker-index.md) için kalıcı teslim ve ana inceleyici kanıtlarını tutar. Düzen `/home/kaan/sloplab/docs/reviews/issue-05` örneğini izler.

Her teslim için iki ayrı parça vardır:

```text
docs/reviews/llm-benchmark/
  <ID>/
    README.md
    commands.jsonl
    comparisons.md
    hashes-start.txt
    hashes-end.txt
    delivery.diff
    run-outputs.sha256
    logs/
    helpers/                 # yalnız gerçekten gerekiyorsa
    <teslime-ozel-sozlesme>
  <ID>-acceptance.md         # yalnız ana inceleyici yazar
```

Worker kanıt paketi, kabul kararı değildir. Ana inceleyici worker'ın günlüklerini okumakla yetinmez; seçilmiş kontrolleri yeni geçici dizinde yeniden çalıştırır ve kendi bulgularını `<ID>-acceptance.md` dosyasına yazar. Kabul edilen kapsam, fazın tamamından daha darsa başlıkta ve durumda açıkça belirtilir.

Henüz yürütülmemiş teslimler için tarih, test sonucu, hash veya kabul kaydı uydurulmaz. `_templates/` dosyaları kopyalanıp gerçek verilerle doldurulur. E4 insan kayıtları bu dizine özet/provenance olarak girebilir; yetkili annotation verisinin yerine geçmez. Blind key ve hassas içerik buraya kopyalanmaz.

İlk aktif kanıt dizini [E0](E0/README.md)'dır.

Kampanya 2026-09-10 tarihinde insan girdisi ve iki gerçek rater bulunmadığı için dondurulmuştur. Güncel durum, bütünlük hashleri ve yeniden başlatma sırası için [proje dondurma kaydını](PROJECT-FROZEN-2026-09-10.md) okuyun.
