# E2a-R1 — Ana inceleyici kararı

Tarih: 2026-09-10. İnceleyici: Sol. Durum: **REVISION REQUIRED. E2a-R1 KABUL EDİLMEDİ.**

## Doğrulanan düzeltmeler

[E2a-R1 briefindeki](../../llm-benchmark-E2a-r1-task.md) dört teknik karşıörnek büyük ölçüde
kapatılmıştır:

- Context ve KEEP kapıları iki dolu, farklı `reviewer_id`, timestamp ve
  agreement/adjudication kanıtını arar; role-only ve aynı-ID kayıtları reddeder.
- KEEP writer, karar CLI'ı ve validator status/gate ikilisi yerine blind item üzerinden ortak
  `keep_gate_blockers` sonucunu kullanır.
- Gate sonucu eksik, bilinmeyen veya category + adjudicated valence yeniden hesabıyla uyuşmazsa
  KEEP fail-closed reddedilir; tutarlı FAIL için “never waived” korunur.
- Validator, context `NOT_STARTED` dışındaysa tam iki-rater kanıtı arar; PARTIAL/unresolved veya
  bozuk provenance ile açılmış context'i yakalar.
- Batch ret yolundaki bellek-içi atomicity korunmuştur.

Worker'ın 141 hedefli ve 381 tam-suite testi bağımsız tekrarlandı; hepsi geçti. Sekiz komut
kaydı, log hedefleri, `run-outputs.sha256`, bağlantılar ve `git diff --check` doğrulandı.
Frozen artefaktlar, stimulus ve append-only audit geçmişleri değişmedi.

## Bloklayıcı eksikler

### R1 — Phase completion hâlâ yalnız status alanına güveniyor

`validate()` sonundaki `phase_complete` kontrolü her blind item için yalnız
`annotation_status == ADJUDICATED` koşulunu arıyor; yeni kanıt-temelli eligibility fonksiyonunu
kullanmıyor. Bellek-içi karşıörnekte 50 blind kaydın rater kanıtlarını boş/eksik bırakıp yalnız
statuslarını `ADJUDICATED`, 50 QC kararını gerekçeli `REJECT` ve `phase_complete=true` yaptığımda
`validate_blind()+validate()` sıfır hata döndürdü. Bu, AGENTS.md'deki Phase 7G tamamlanması için
iki gerçek bağımsız rater şartını ihlal eder.

Phase completion, karar KEEP/REVISE/REJECT olsa da her item için tam iki-rater
agreement/adjudication kanıtı aramalıdır. Status alanı tek başına yeterli olmamalı; eksik veya
aynı kimlikli slotlar, unresolved akış ve eksik adjudication phase completion'ı engellemelidir.

### R2 — Yeni testler yasaklanmış pozitif sentetik rater kayıtları üretiyor

Revizyon briefi “pozitif iki-rater kaydı uydurma” demesine rağmen
`tests/test_phase7g_gates.py`, `_synthetic_eligible_shape`, `test_agreement_shape_is_eligible`,
`test_adjudicated_shape_is_eligible` ve `ADJUDICATED+PASS` yolu ile sentetik reviewer ID,
valence, timestamp ve pozitif eligibility kaydı oluşturuyor. “SYN” etiketi bu kayıtları insan
anotasyonu olmaktan çıkarmaz. Bu hem briefin hem AGENTS.md'deki yapay blind-rater anotasyonu
yasağının dışındadır.

Yeni pozitif sentetik kayıtlar kaldırılmalıdır. Güvenlik regresyonları yalnız negatif yapısal
ihlaller, saf helper bağımlılıkları için mock/stub veya depoda önceden yetkilendirilmiş fixture
varsa ona salt-okunur referansla sınanmalıdır. Gerçek pozitif iki-rater ve adjudication E2E yolu
insan girdisi gelene kadar açık kabul örneği kalmalıdır.

## Karar ve devam

R1 teknik kapı açığıdır; R2 araştırma bütünlüğü ihlalidir. Ham E2a-R1 teslimi korunacaktır.
[E2a-R2 briefi](../../llm-benchmark-E2a-r2-task.md) yalnız phase-completion kanıtı ve test fixture
temizliğiyle sınırlıdır.
