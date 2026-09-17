# E2a-R2 — Phase 7G kapı sözleşmesi (gate-contract, R2 güncel)

**Statü: UYGULANAN KOD + KANIT.** `../E2a/gate-contract.md` ve `../E2a-r1/gate-contract.md`
değişmedi; bu dosya güncel sözleşmedir. Frozen kuralları uygular; E2b/E2c rubriği ve üretim
verisi değişmez. Bilimsel karar içermez.

## 1. Kapı matrisi (fail-closed, kanıt-temelli)

`record_context` = bağlam kaydı, `record_decision(KEEP)` = final KEEP,
`validator` = onay + ordering + completion değişmezleri, CLI = sihirbazlar.
Parantez: hangi kanıtın eksik olduğu.

| Blind kayıt | record_context | record_decision KEEP | validator | CLI |
| --- | --- | --- | --- | --- |
| PENDING | RET | RET | hata (sıralama + onaysız anotasyon) | listelemez |
| PARTIAL (canlı dahil) | RET | RET | hata (two-rater) | listelemez |
| DISAGREEMENT çözümsüz | RET | RET | hata (two-rater) | KEEP teklif etmez |
| Provenance eksik / aynı ID / rol-only | RET | RET | hata (two-rater) | KEEP teklif etmez |
| Gate eksik/bilinmeyen/uyuşmaz | RET (kapı değilse AÇIK*) | RET | hata (kapı) | KEEP teklif etmez |
| Gate FAIL (tutarlı) | AÇIK (F6 bilimsel sonuçtur) | RET (never waived) | hata (never waived) | KEEP teklif etmez |
| Gate PASS/REVIEW (tutarlı) | AÇIK | AÇIK (diğer kapılar tamamsa) | temiz | teklif eder |

`*` Context kapısı gate sonucuna bakmaz; yalnız kayıt bütünlüğüne.

## 2. Ortak sınır (tek implementasyon)

`blind_item_eligible_for_context` (slot kanıtı + farklı kalıcı ID + uzlaşma/adjudication),
`keep_gate_blockers` (kanıt + `evaluate_gate` tutarlılık + PASS/REVIEW zorunluluğu),
`keep_eligibility`, `blind_item_for`/`blind_gate_for`/`category_for`. Status/gate-ikilisi
helper'ı kaldırıldı. `expected_valence` kullanılmaz (Layer A hipotezidir).

## 3. Phase completion (R1)

`phase_complete=true`, karar türünden (KEEP/REVISE/REJECT) bağımsız olarak her blind kayıtta
tam kanıt ister. Ek olarak `validate_blind`, ADJUDICATED status ile slot/kanıt tutarsızlığını
fail-closed raporlar. İkisi de ortak helper'ı kullanır; paralel mantık yoktur.

## 4. Ret bütünlüğü + bağımsızlık non-claim (korundu)

`_atomic` geri alma; dosya/snapshot/history yalnız başarı sonrası. Farklı ID'ler bilişsel
bağımsızlık kanıtı değildir. Canlı BLIND-001 (rol-only) kapıyı geçemez; ID uydurulmadı.

## 5. Fixture etiği (R2)

- E2a/E2a-R1 zincirinde eklenen pozitif sentetik kayıtlar KALDIRILDI: `_synthetic_eligible_shape`
  helper'ı, iki eligible-shape True testi ve ADJUDICATED+PASS başarı yolu yok.
- Negatif yapısal vektörler (canlı PENDING/PARTIAL, boş-slot el-status, aynı-ID, eksik/bilinmeyen/
  uyuşmaz gate) + eligibility stub'ları (boolean) + FAIL yeniden-hesap stub'ı korunur; stub'lar
  insan annotation payload'ı üretmez (SYN yer tutucuları anlamsızdır, atıfsızdır, yazılmaz).
- Gerçek pozitif iki-rater/adjudication E2E yolu açık kabul örneğidir (insan girdisiyle).

## 6. R2-delta (E2a-R1 → E2a-R2)

Eklenen: completion kanıt kontrolü (`validate` + `validate_blind`, ortak helper) + zorunlu
karşıörnek testi (50×ADJUDICATED-boş-slot + 50 gerekçeli REJECT + complete → hata).
Kaldırılan: pozitif sentetik helper/testler/yollar. Korunan: context/KEEP/gate/atomicity/CLI
davranışları, fixture disiplini.

## 7. Değişen dosyalar

- `scripts/validate_phase7g_review.py`: completion + blind-paket kanıt kontrolleri.
- `scripts/apply_phase7g_annotations.py`: değişiklik YOK (R1 kapıları aynen kullanıldı).
- `tests/test_phase7g_gates.py`: fixture temizliği + stub wiring + karşıörnek (29 test).
- `tests/test_phase7g_qc.py`: 1 test (rol-only uzlaşma artık kanıt hatası verir).
- Üretim QC/audit JSON'ları, mühürlü belgeler, stimulus, insan rating'leri değişmedi.
