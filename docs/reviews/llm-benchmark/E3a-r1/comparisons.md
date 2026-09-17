# E3a-R1 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty: `M .gitignore` + E2a zinciri kod değişikliği (commitlenmedi, ayrı teslimler);
  untracked: brief/plan + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E3a-r1 dizini iskeletti.
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok.
- Önceki kabul: `../E3a-acceptance.md` (R1–R3). Harita `revision-map.md`'dedir.
- Geçici çalışma: `mktemp -d` gerçek dizini (yeniden üretim çıktısı; 03 logunda yol).

## Dosya ve hash farkları

Beklenen farklar (`E3a-r1` belge + helper teslimi):

- `docs/reviews/llm-benchmark/E3a-r1/` altında 9 belge + `helpers/e3a_scan.py` + `logs/`
  (7 komut). Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: v1 hash + 50/171 + final-byte + audit prefix
  birebir aynı; yalnız dosya listesi satırı değişti (beklenen).
- `../E3a/` teslimi değişmedi (05 logundaki değişmezlik kontrolü).

Beklenmeyen farklar: yok.

- Stimulus v1, content kaynakları, QC/audit, testler, kod değişmedi.
- `git diff --check`: temiz. `delivery.diff`: tracked fark YOKTUR (salt belge+helper işi).

## Davranış karşılaştırması

- Kalıcı helper temp-output'ta teslim JSON'uyla bayt-eşit envanter üretir (03 logu).
- 6 R-REF hash'i frozen metinden bağımsız doğrulandı; kanıtlarda alıntı yok.
- Sayılar yeniden hesaplandı: 50/171, 50/50, 29/21, 7/43, 19 aday (E3a ile aynı).
- Hedefli phase7f testleri salt okunur geçti (04 logu).

## Açıklanmayan farklar

Yok.
