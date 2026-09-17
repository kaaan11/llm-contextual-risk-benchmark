# E2a-R2 — Revizyon haritası (revision map)

E2a-R1 acceptance R1–R2'nin `E2a-r2` karşılığı. `../E2a/`, `../E2a-r1/` kanıtları değişmedi.
Korunanlar: E2a-R1'in context/KEEP/gate/atomicity/CLI davranışları ve negatif-vektör disiplini.

| Blokaj | E2a-R1 kusuru | Düzeltme (dosya/bölüm) | Kabul karşılama |
| --- | --- | --- | --- |
| R1 completion | `phase_complete` yalnız status'e bakıyordu | `validate()`: her kayıtta ortak helper kanıtı (karar-bağımsız); `validate_blind()`: ADJUDICATED-kanıt tutarsızlığı hatası; paralel mantık yok | 50×ADJUDICATED-boş-slot + 50 REJECT + complete → blind + completion hataları (valence/ID eklenmedi) |
| R2 fixture | Pozitif sentetik helper/test/yol vardı | Kaldırıldı: `_synthetic_eligible_shape`, 2 True testi, PASS başarı yolu. Wiring stub'larla (boolean/gate stub; insan payload'ı yok); SYN yer tutucuları anlamsız | Kaynak taramasında pozitif sentetik helper/kayıt yok; True-yol bilerek test edilmedi (gerekçe §5) |

## Korunanlar (yeniden tasarım yok)

- E2a-R1 kapı matrisi gövdesi, `_atomic`, non-claim, CLI sınırları, E2b/E2c sınırları.
- Mevcut suite'in yerleşik F-06 fixture örüntüsü (rol-only kayıt + ayrı kanıt iddiasızlığı)
  aynen durur; rol-only uzlaşmanın kanıt hatası vermesi 1 testte belgelendi.

## Etkilenen dosyalar

- Değişen (kod): `scripts/validate_phase7g_review.py`.
- Değişen (test): `tests/test_phase7g_gates.py`, `tests/test_phase7g_qc.py` (1 test).
- Değişmeyen: `../E2a/*`, `../E2a-r1/*`, writer/CLI scriptleri, diğer testler, mühürlü
  belgeler, stimulus, audit/QC, rating'ler.
