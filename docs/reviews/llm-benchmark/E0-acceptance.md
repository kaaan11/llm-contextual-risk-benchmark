# E0 — Ana inceleyici kabul kararı

Tarih: 2026-09-09. İnceleyici: Sol. Durum: **E0 KABUL EDİLDİ. Uygulama ve bilimsel karar fazları açıktır.**

## İnceleme ve bağımsız kanıt

[E0 briefi](../../llm-benchmark-E0-task.md), worker README'si, P01–P15 + S01/S02 bulgu matrisi, test güvenliği sınıflandırması, provenance sınırı, başlangıç/bitiş hashleri, komut defteri ve bütün loglar incelendi. E0 yalnız belge/kanıt paketidir; üretim kodu, protokol, stimulus, QC veya audit kaydı değiştirmemiştir.

Ana inceleyici tarafından salt okunur yeniden hesaplanan sonuçlar:

- Altı manifest protocol dosyasının per-file hashleri ve composite `47ae3fed4117639ef2575135a6ca63f000f4fcc8c052c629355f6ccf4bbcfc6f` eşleşiyor.
- Stimulus SHA-256 `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`; 50 madde, 171 koşul, dört grup ve 50/50 item içi final-byte eşitliği doğrulandı. Gerçek D anahtarı 21 maddede var.
- Blind durum 49 `PENDING` + 1 `PARTIAL_ONE_RATER`; `rater_a=1`, `rater_b=0`. Nihai 50 kararın tamamı `PENDING`; Phase 7G kapalıdır.
- `phase7e_review_history.jsonl` 51 satır / `e145afed…`; `phase7g_review_history.jsonl` 5 satır / `23755e0f…`. Worker başlangıç kayıtlarıyla aynı; append-only geçmişte değişiklik yok.
- Hakem ZIP SHA-256 değeri `1c7c12ed…`; ZIP içindeki yedi manifest girdisinin boyut ve hashleri doğrudan ZIP'ten yeniden doğrulandı.
- Teslim içi Markdown bağlantılarında eksik hedef yok ve `git diff --check` temiz.

Ana inceleyici güvenli hedefli testleri mevcut `.venv` üzerinden yeniden çalıştırdı:

```bash
.venv/bin/pytest -p no:cacheprovider \
  tests/test_dataset_validation.py \
  tests/test_phase7f_stimulus.py \
  tests/test_phase7g_tooling.py \
  tests/test_benchmark_framework.py \
  tests/test_phase8_dryrun.py
python3 scripts/validate_phase7e_review.py
python3 scripts/validate_phase7g_review.py
git diff --check
```

Sonuç: **81 test geçti**. Phase 7E validator `VALID — 50 items, 0 pending, 50 approved`; Phase 7G validator `VALID — pending=50, keep=0, approved=0, phase_complete=False`. İlk `uv run --offline --frozen pytest ...` denemesi test toplamadan önce setuptools editable-build hatasında durdu: flat layout içinde birden çok top-level package bulundu. Bu test başarısızlığı değildir; mevcut `.venv/bin/pytest` ile aynı güvenli hedefler başarıyla yürütüldü.

Tam offline suite çalıştırılmadı. Bazı test yolları sentetik kör-rater değerleri oluşturuyor; kök `AGENTS.md` ajanların sentetik/sahte rater anotasyonu üretmesini yasaklıyor. E0'ın üretim davranışı değiştirmeyen salt-okunur kapsamı için tam suite eksikliği kabulü engellemez. Sonraki kod paketlerinde ilgili testler bu sınır gözetilerek seçilecek; insan-semantiği isteyen pozitif yollar insan girdisi olmadan uydurulmayacak.

## Kabul ölçütleri

| Ölçüt | Kanıt | Sonuç |
| --- | --- | --- |
| Kaynaklar ve farklı koşu beyanları ayrılmış | `findings.md`, `baseline.md`, `provenance-scope.md` | PASS |
| P01–P15 ve S01/S02 durum/yöntem/sınır/sahip matrisi | `findings.md` | PASS |
| Testlerin ağ, gerçek QC yazımı ve sentetik-rater riski sınıflandırılmış | `test-safety.md`; ana inceleyici statik kontrolü | PASS, aşağıdaki sınırla |
| Blind key yalnız varlık düzeyinde ele alınmış | `baseline.md`, `provenance-scope.md`, hashes dosyaları | PASS |
| Hash, commit, lisans, overlap ve contamination ayrılmış | `provenance-scope.md` | PASS |
| Frozen composite, stimulus, QC sayıları ve audit prefix korunmuş | Worker başlangıç/bitiş kayıtları + bağımsız hesap | PASS |
| Üretim/QC/API davranışı değiştirilmemiş | Git durumu, diff ve dosya kapsamı | PASS |

## Worker kanıt paketindeki kusurlar

Worker'ın ham kanıtı değiştirilmeden korunmuştur. İki küçük teslim kusuru vardır:

1. `commands.jsonl` içinde 2. satır boştur; bu nedenle dosyanın her fiziksel satırı strict JSON olarak parse edilemez. Boş satır atlandığında bir şema notu ve **15 geçerli command kaydı** vardır; tüm kayıtların exit code'u 0 ve stdout/stderr/combined hedefleri mevcuttur. Worker README'sindeki “1 şema notu + 11 komut” ifadesi yanlıştır; tablo fiilen 15 komut gösterir.
2. `run-outputs.sha256`, son üretim komutunun kendi stdout dosyasını da kapsar. Bu stdout dosyası hash listesi hesaplandıktan sonra büyüdüğü için `logs/15-run-outputs-final.sh.stdout` checksum'u doğrulanamaz; diğer listelenen girdiler doğrulanır. Bu self-reference kanıt tasarımı sonraki teslimlerde kullanılmamalıdır.

Bu kusurlar E0'ın bilimsel/bütünlük sonuçlarını değiştirmiyor: kritik hashler ve durumlar ana inceleyici tarafından kaynak dosyalardan yeniden hesaplandı. Bu nedenle worker evidence paketi geriye dönük düzeltilmeden E0 kabul edildi. Sonraki brieflerde komut defteri boş satırsız yazılmalı; çıktı manifestosu kendi üretim logunu veya kendisini kapsamamalıdır.

## Karar, sınırlar ve devam

E0'ın amacı olan başlangıç referansı, bulgu matrisi, test güvenliği ve provenance sınırı yeterli ve incelemeye elverişlidir. Raporun dinamik P14/P15 karşıörnekleri bu kabulde yeniden üretilmiş sayılmaz; dış literatür, commit authentication, dış overlap ve contamination yokluğu açık kalır. `pytest` paket discovery sorunu ayrıca sonraki mühendislik işi olarak ele alınabilir, fakat E0 kapsamına kod düzeltmesi eklenmedi.

Sıradaki önerilen worker paketi [E1a — araştırma iddiası ve karar matrisi taslağı](../../llm-benchmark-E1a-task.md). E0 kabulü ayrıca E2a ve E3a önkoşulunu açar; aynı anda tek teslim çalışma düzeninde önce E1a ilerletilecektir. E0 kabulü E1'in, Phase 7G'nin veya Phase 8'in tamamlandığı anlamına gelmez.

