# E2a-R1 — Revizyon haritası (revision map)

E2a acceptance R1–R4'ün `E2a-r1` karşılığı. `../E2a/` kanıtı değişmedi. Korunanlar: E2a'nın
PARTIAL-ret, FAIL-ret, atomicity, CLI-sınır davranışları ve fixture etiği disiplini.

| Blokaj | E2a kusuru | Düzeltme (dosya/bölüm) | Kabul karşılama |
| --- | --- | --- | --- |
| R1 kanıt | KEEP yalnız status/gate'e bakıyordu | `keep_gate_blockers` (slot+provenance+akış+gate-tutarlılık); writer/validator/CLI aynı fonksiyon | Boş-slot + el-status: writer ret, validator hata, CLI gizler |
| R2 kimlik | Rol yeterliydi; ID farkı yoktu | `_slot_proven` ID zorunlu; eligibility'de ID farkı; `blind_keep_blockers` kaldırıldı | Aynı-ID: context/KEEP/validator ret; rol-only geçemez |
| R3 ordering | Yalnız PENDING kontrolü | Context açıksa tam kanıt aranır (PARTIAL/çözümsüz/provenance/ID/eşlemesiz hata) | PARTIAL + COMPLETE validator hatası |
| R4 gate | Eksik/bilinmeyen/uyuşmaz gate geçerdi | `evaluate_gate` yeniden hesabı; KEEP yalnız tutarlı PASS/REVIEW; FAIL/eksik/bilinmeyen/uyuşmaz ret | 4 gate durumu: KEEP ret + validator hata |

## Korunanlar (yeniden tasarım yok)

- E2a kapı matrisi gövdesi, `_atomic`, bağımsızlık non-claim, test stratejisi, E2b/E2c sınırları.
- Etkilenen legacy/tests: `test_phase7g_gates.py` yeni imzalar + 5 karşıörnek grubu.

## Etkilenen dosyalar

- Değişen (kod): 4 script (yeni imzalar, ölü helper kaldırıldı).
- Değişen (test): `tests/test_phase7g_gates.py` (31 test).
- Değişmeyen: `../E2a/*`, diğer test dosyaları, mühürlü belgeler, stimulus, audit/QC, rating'ler.
