# E2a — Phase 7G kapıları ve durum geçişleri

Durum: [E2a-R2 ile kabul edildi](reviews/llm-benchmark/E2a-r2-acceptance.md). Sahip: küçük worker.  
Önkoşul: E0 kabulü. Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Tek paket hedefi

Mevcut frozen kuralları uygulayan fail-closed QC kapılarını düzelt: tek rater sonrası context açılmasın ve blind gate `FAIL` olan madde `KEEP` olamasın. Yeni rubrik, D alanları ve Layer-B şeması E2b/E2c kapsamıdır.

## Kod kapsamı

Oku/değiştir: `scripts/apply_phase7g_annotations.py`, `scripts/validate_phase7g_review.py`, gerekirse `scripts/review_context.py`, `scripts/decide_phase7g.py` içindeki ortak eligibility kullanımı ve doğrudan ilgili `tests/test_phase7g_qc.py`, `tests/test_phase7g_tooling.py`. Küçük ortak saf eligibility fonksiyonu eklenebilir.

Üretim QC/audit JSON'larına yazma. Existing human rating'i değiştirme. Sentetik kör-rater annotation üretme. Frozen protokoldeki `FAIL is never waived` kuralını uygula; kural değişikliği tasarlama.

## Davranış sözleşmesi

- Context eligibility iki bağımsız, farklı insan kimliğine bağlı rating ve agreement/adjudication ile tamamlanan statü ister; `PARTIAL_ONE_RATER`, PENDING, unresolved disagreement ve eksik provenance reddedilir.
- Blind `gate_result=FAIL`, decision writer ve validator katmanlarında KEEP'i reddeder. Mevcut yanlış durum dosyadan yüklenirse validator hata verir.
- CLI listesi ile doğrudan kayıt API'si aynı ortak sınırı uygular.
- Ret edilen işlem input nesnesi/dosyası, snapshot ve history üzerinde değişiklik yapmaz.
- Kimlik alanlarının farklı olması bilişsel bağımsızlığın kanıtı diye raporlanmaz.

## Kabul testleri

Gerçek annotation semantiği üretmeden PENDING/partial/FAIL ve yapısal olarak eksik durumları reddeden testler yaz. Pozitif iki-rater geçişi mevcut yetkili fixture olmadan sınanamıyorsa yeni sahte label uydurma; bunu ana inceleyici kabul örneği olarak açık bırak. Validator ile writer tutarlılığı, mutation olmaması ve CLI görünürlüğü sınanır. İlgili hedefli testler, gerekirse tam offline suite, `git diff --check` ve bütünlük kontrolleri çalıştırılır.

Teslim: `docs/reviews/llm-benchmark/E2a/` içinde `gate-contract.md` dahil kanıt paketi. E2a bitince E2'nin tamamını veya insan QC'yi hazır ilan etme.
