# E2b — B/C/D görünürlüğü ve context-review tamlığı

Durum: E2a ve onaylı E1 alan sözleşmesini bekliyor. Sahip: küçük worker.  
Ortak kurallar: [worker sözleşmesi](llm-benchmark-worker-contract.md).

## Hedef

Context sihirbazının gerçek `neutral_filler_control` koşullarını göstermesini ve yalnız uygulanabilir bütün alanlar tamamlandığında `COMPLETE` üretmesini sağla. Layer-B referans saklama E2c'ye aittir.

## Kod kapsamı

Oku/değiştir: `scripts/review_context.py`, `scripts/apply_phase7g_annotations.py`, `scripts/build_phase7g_review.py`, `scripts/validate_phase7g_review.py` ve doğrudan Phase 7G testleri. Onaylı E1b applicability tablosunu salt okunur sözleşme olarak kullan.

Stimulus metni ve yetkili QC verisi değişmez. CLI çalıştırmasını gerçek audit yollarına yöneltme; geçici kopya veya saf fonksiyonlarla doğrula.

## Davranış ve kabul

- 21 gerçek D koşulu doğru anahtarla bulunur ve condition code/name doğrulanır; D'siz 29 maddeye sahte D yaratılmaz.
- B/C için relevance, direction, resolution, leakage ve naturalness/safety; D için onaylı contamination/length alanları görünürdür.
- Uygulanamaz alanlar açık N/A politikasıyla taşınır. Eksik uygulanabilir alan, not veya D incelemesi `COMPLETE` olamaz.
- Quit/validation failure durumunda yarım form tamamlanmış görünmez; append olayı yalnız geçerli atomik kayıt sonrası oluşur.
- Builder, writer, validator ve CLI aynı required-field sözleşmesini paylaşır.

Hedefli testlerde D sayısı/görünürlüğü, D'siz yol, kısmi payload, note zorunluluğu, quit ve mutation yokluğu bulunur. Sentetik insan yargısı üretme; alan tamlığı fixture'ı değerlerin bilimsel anlamına karar vermeyen yapısal veriyle sınırlı olmalıdır. Teslimde `context-contract.md` ve kanıt paketi bırak, sonra dur.

