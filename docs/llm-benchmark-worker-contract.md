# LLM Benchmark — Worker teslim ve kanıt sözleşmesi

Bu belge bütün `llm-benchmark-*-task.md` briefleri için bağlayıcı ortak sözleşmedir. Çelişkide kök [AGENTS.md](../AGENTS.md), ardından aktif görev briefi ve üst plan uygulanır.

## Başlangıç

1. `AGENTS.md`, aktif brief, üst planın yalnız ilgili fazı ve briefte belirtilen kabul kayıtlarını oku.
2. `git status --short`, `git rev-parse HEAD`, Python ve gerekli araç sürümlerini teslim günlüğüne kaydet. Önceden var olan `.gitignore`, `uv.lock` ve diğer kullanıcı değişikliklerini sahiplenme veya düzeltme.
3. Teslim dizini doluysa üzerine yazma; ana inceleyiciye durumu bildir. Başlangıç kanıtını sonradan uydurma.
4. İzinli dosyaları `rg` ile incele. Kapsam başka bir teslimin sözleşmesini gerektiriyorsa dur; o işi bu pakete çekme.

## Değişmez sınırlar

- Mühürlü protokol belgelerini, `dataset/pilot/multiturn/stimulus_dataset_v1.json` dosyasını ve 171 stimulus metnini değiştirme.
- `results/dataset_audit/*.jsonl` geçmişini silme veya yeniden yazma. Testleri gerçek audit/QC dosyalarına yazdırma.
- İnsan annotation'ı, Layer-B referansı, adjudication veya KEEP kararı üretme. İnsan kimliği ya da bağımsızlık beyanı uydurma.
- Phase 7G kapanmadan gerçek model/API çağrısı yapma. Provider anahtarı, credential, blind key içeriği, ham hassas yanıt veya tam exception metnini teslim paketine kopyalama.
- Bilimsel kararı kod tercihiyle kapatma. Onay bekleyen metin `DRAFT / NOT EFFECTIVE` kalır.
- Commit, push, branch değiştirme, bağımlılık yükseltme veya yeni genel framework yok. Açıkça izin verilen küçük modül dışında mimari kapsamı büyütme.

## Test ve veri kuralları

Test çıktıları `/tmp` altında `mktemp -d` ile oluşturulan gerçek dizine yazılır. Mock transport ve matematiksel sentetik satırlar açıkça fixture olarak işaretlenir; gerçek QC veya ampirik model sonucu gibi sunulmaz. AGENTS.md sentetik kör-rater anotasyonu üretmeyi yasakladığından, böyle veri isteyen test yazma veya çalıştırma; durum geçişleri mümkünse boş/eksik kayıtlarla, saf doğrulama fonksiyonlarıyla ya da rater semantiği taşımayan yapısal fixture'larla sınanır. Bunun mümkün olmadığı kabul örneğini ana inceleyiciye açık bırak.

Değişiklik riskiyle orantılı hedefli testleri çalıştır. Kod tesliminde ilgili testler ve `git diff --check` zorunludur; tam offline suite yalnız brief istiyorsa veya hedefli değişiklik geniş sözleşmeyi etkiliyorsa bir kez çalıştırılır. Ağ veya eksik bağımlılık engeli test başarısızlığı diye gizlenmez.

Başlangıç ve bitişte şunları yeniden doğrula:

- protokol manifestosundaki per-file ve composite hash;
- stimulus v1 hash'i ve 50/171 sayıları;
- append-only audit dosyalarının başlangıç prefix'i;
- kullanıcıya ait başlangıç değişikliklerinin korunması.

## Teslim düzeni

Her worker `docs/reviews/llm-benchmark/<ID>/` altında şu kanıtları bırakır:

- `README.md`: sonuç, değişen dosyalar, doğrulamalar, sınırlılıklar ve `tamamlandı/kısmi` durumu;
- `commands.jsonl`: gerçek komut, cwd, başlangıç/bitiş zamanı, exit code, stdout/stderr yolu;
- `comparisons.md`: başlangıç/bitiş hashleri, davranış karşılaştırmaları ve açıklanan farklar;
- `hashes-start.txt`, `hashes-end.txt`, `delivery.diff`, `run-outputs.sha256` gerektiği ölçüde;
- `logs/`: kalıcı stdout/stderr ve gerçek exit kayıtları;
- briefin istediği sözleşme veya envanter belgesi.

Untracked dosyalar düz `git diff` içinde görünmez; teslim README'sinde ayrıca sayılır. Günlükte çalıştırılmayan komut bulunmaz. Geçici yol, test sayısı ve hangi kontrollerin worker tarafından yapılmadığı açık yazılır.

Worker `<ID>-acceptance.md` oluşturmaz ve üst planın durumunu kabul edildi diye değiştirmez. Ana inceleyici diff'i, kritik kabul örneklerini, korunan hashleri ve audit prefix'ini bağımsız doğrulayıp [kabul şablonuyla](reviews/llm-benchmark/_templates/acceptance.md) karar verir.

## Durma noktası

Aktif ID bittiğinde dur. Sonraki teslimi, gerçek insan sürecini veya canlı Phase 8'i başlatma. Son mesajda tamamlanan kapsamı, açık kalanları ve sıradaki önkoşulu yaz.

