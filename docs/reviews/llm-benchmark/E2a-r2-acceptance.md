# E2a-R2 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **ACCEPTED. E2a KOD ZİNCİRİ KABUL EDİLDİ.**

## Kabul edilen kapsam

[E2a-R2 briefindeki](../../llm-benchmark-E2a-r2-task.md) iki blokaj kapatılmıştır.

- `validate_blind`, `ADJUDICATED` statusunu tam iki-rater kanıtı olmadan kabul etmez ve ortak
  `blind_item_eligible_for_context` helper'ını kullanır.
- `phase_complete=true`, final karar KEEP/REVISE/REJECT ayrımı yapmadan 50 blind kaydın her
  birinde iki dolu, farklı kalıcı insan kimliği, timestamp ve agreement/tamamlanmış adjudication
  kanıtı arar. Status alanı tek başına yeterli değildir.
- E2a-R1'de eklenen pozitif sentetik eligible helper, agreement/adjudication True testleri ve
  PASS başarı yolu kaldırılmıştır. Kalan yeni testler negatif yapısal ihlal vektörleri veya insan
  payload'ı üretmeyen boolean/gate stub'larıdır.
- E2a-R1'in context/KEEP kanıt kapıları, gate yeniden hesabı, FAIL→KEEP yasağı, CLI sınırları ve
  ret atomicity davranışları korunmuştur.

Gerçek pozitif iki-rater ve adjudication E2E yolu, yalnız gerçek insan girdisiyle sınanabilecek
açık kabul örneğidir. Bu sınırlılık E2a'nın fail-closed kod düzeltmesini engellemez ve Phase 7G
kapısını açmaz.

## Bağımsız kanıt

- Zorunlu bellek-içi karşıörnek, 50 boş/eksik slotlu `ADJUDICATED` kayıt ve 50 gerekçeli REJECT
  ile `phase_complete=true` durumunda 51 ilgili validator hatası üretti.
- 139 hedefli test ve 379 testlik tam offline suite geçti.
- Phase 7E ve Phase 7G canlı validator'ları geçti; Phase 7G `phase_complete=False`,
  `inter_rater=not_available` kaldı.
- Sekiz komut kaydı, log hedefleri, `run-outputs.sha256`, belge bağlantıları ve
  `git diff --check` doğrulandı.
- Stimulus SHA-256 değeri `2f78e79e19d844b84b6bc06a0c2bef47e19283cc7c54b91f6ae283e1a74af077`
  olarak kaldı. Audit geçmişleri 51 ve 5 satırla `e145afed…` ve `23755e0f…` hashlerinde kaldı.
  Frozen artefaktlara, üretim QC/audit kayıtlarına veya insan rating'lerine yazılmadı.

## Karar ve sonraki teslim

E2a-R2 için yeni worker revizyonu gerekmiyor. E2b, insan tarafından onaylanmış E1 alan
sözleşmesini beklediği için henüz aktif değildir. E0 kabulüne bağlı ve stimulus üzerinde salt
okunur çalışan sıradaki bağımsız teslim [E3a](../../llm-benchmark-E3a-task.md)'dır.
