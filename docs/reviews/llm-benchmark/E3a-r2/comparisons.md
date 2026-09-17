# E3a-R2 — Başlangıç/bitiş karşılaştırması

## Referanslar

- Başlangıç HEAD ve çalışma ağacı: `9dd9d31607b3d97c02fe3ef9b7cfb68b4a3ed50e`, branch `master`,
  tracked dirty: `M .gitignore` + E2a zinciri kod değişikliği (commitlenmedi, ayrı teslimler);
  untracked: brief/plan + `docs/reviews/` + `uv.lock`
  (`logs/01-git-head-status.sh.stdout`, `hashes-start.txt`). E3a-r2 dizini iskeletti.
- Bitiş HEAD ve çalışma ağacı: aynı HEAD; commit/push/branch yok.
- Önceki kabul: `../E3a-r1-acceptance.md` (R1–R2). Harita `revision-map.md`'dedir.
- Geçici çalışma: `mktemp -d` gerçek dizini (03 logunda yol).

## Dosya ve hash farkları

Beklenen farklar (`E3a-r2` belge + helper teslimi):

- `docs/reviews/llm-benchmark/E3a-r2/` altında 9 belge + `helpers/e3a_scan.py` + `logs/`
  (9 komut). Untracked oldukları için düz `git diff` içinde görünmezler; burada sayıldılar.
- `hashes-start.txt` → `hashes-end.txt`: v1 hash + 50/171 + final-byte + audit prefix
  birebir aynı; yalnız dosya listesi satırı değişti (beklenen).
- `../E3a/`, `../E3a-r1/` teslimleri değişmedi (07 logundaki değişmezlik kontrolü).

Beklenmeyen farklar: yok.

- Stimulus v1, content kaynakları, QC/audit, testler, kod değişmedi.
- `git diff --check`: temiz. `delivery.diff`: tracked fark YOKTUR.

## Davranış karşılaştırması

- Kalıcı helper temp-output'ta teslim JSON'uyla bayt-eşit envanter üretir.
- Exact 7/43 (tümü AM) + ayrım unit örneği + 3 refusal kanıtı (içerik değişmedi).
- R-REF 6/6 hash, 19 aday, 50 phase7f testi, frozen/audit korunması.

## Açıklanmayan farklar

Yok.
